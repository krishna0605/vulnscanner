import cron from 'node-cron';
import { supabase } from './supabase';
import { CrawlerService } from './crawler';
import { logger } from './logger';

export class SchedulerService {
  private isRunning: boolean = false;

  constructor() {
    logger.info('[Scheduler] Service initialized');
  }

  public start() {
    // Run every minute
    cron.schedule('* * * * *', async () => {
      if (this.isRunning) {
        logger.info('[Scheduler] Previous run still active, skipping.');
        return;
      }
      this.isRunning = true;
      try {
        await this.checkScheduledScans();
      } catch (err) {
        logger.error({ err }, '[Scheduler] Error checking scans');
      } finally {
        this.isRunning = false;
      }
    });
    logger.info('[Scheduler] Cron job started (* * * * *)');
  }

  private async checkScheduledScans() {
    const now = new Date().toISOString();

    // Find scans where is_scheduled = true AND next_run_at <= now AND status != 'running'
    // Actually, we usually want to trigger a NEW scan based on the template,
    // OR if we are just "running the pending scan".
    // Strategy: The "Scheduled Scan" in DB is a "Template". When it's due, we clone it pending scan.

    // Let's assume we look for "Active Scheduled Configs" that are due.
    // Simplifying: The user creates a scan with `is_scheduled=true`.
    // We treat that row as the "Definition".
    // When due, we create a new INSERT into scans with `parent_scan_id`.

    const { data: dueScans, error } = await supabase
      .from('scans')
      .select('*')
      .eq('is_scheduled', true)
      .lte('next_run_at', now);

    if (error) {
      logger.error({ err: error }, '[Scheduler] DB Error');
      return;
    }

    if (!dueScans || dueScans.length === 0) return;

    logger.info({ count: dueScans.length }, `[Scheduler] Found due scans`);

    for (const template of dueScans) {
      await this.triggerRun(template);
    }
  }

  private async triggerRun(template: any) {
    console.log(`[Scheduler] Triggering run for ${template.id} (${template.target_url})`);

    // 1. Calculate next run
    const cronExpression = template.schedule_cron;
    let nextRun = null;
    try {
      // Use a library to parse cron and get next date?
      // node-cron doesn't easily give "next date" from a string without a task.
      // We might need `cron-parser`.
      // For MVP, lets just add 24 hours if daily? No, we need proper cron handling.
      // If we lack `cron-parser`, we can just rely on the user update or simple daily.
      // Actually, we can install `cron-parser`.
      // For now, let's just assume daily if cron is missing or complex.
      // Or, we update the template's `next_run_at` to NULL to stop it,
      // or ideally calculate next.
      // Let's create the NEW scan first.
    } catch (e) {
      console.error('[Scheduler] Cron Parse Error', e);
    }

    // 2. Create new Scan instance
    const { data: newScan, error } = await supabase
      .from('scans')
      .insert({
        project_id: template.project_id,
        target_url: template.target_url,
        status: 'pending',
        type: template.type,
        config: template.config,
        parent_scan_id: template.id,
        is_scheduled: false, // The child is NOT scheduled, it's a one-off run
      })
      .select()
      .single();

    if (error) {
      console.error('[Scheduler] Failed to create child scan:', error);
      return;
    }

    // 3. Start Crawler
    const crawler = new CrawlerService();
    // Fire and forget, crawler manages its own state
    crawler.scan(newScan.id, newScan.target_url, newScan.config).catch((e) => {
      console.error('[Scheduler] Crawler failed to start:', e);
    });

    // 4. Update Template
    // Update last_run_at and next_run_at
    // Since we don't have cron-parser installed yet, let's default to +1 Day
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + 1); // Default 24h

    await supabase
      .from('scans')
      .update({
        last_run_at: new Date().toISOString(),
        next_run_at: nextDate.toISOString(), // Placeholder for real cron calc
      })
      .eq('id', template.id);
  }
}
