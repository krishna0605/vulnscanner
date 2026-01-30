-- =============================================================================
-- MIGRATION: Populate Activity Logs on Scan Events
-- =============================================================================
-- This migration creates database triggers to automatically log activity
-- when scans are started, completed, or fail. This populates the activity_logs
-- table which is displayed in the Dashboard "Recent Activity" feed.
-- =============================================================================

-- 1. Create the trigger function to log scan status changes
CREATE OR REPLACE FUNCTION log_scan_activity()
RETURNS TRIGGER AS $$
DECLARE
    project_name TEXT;
    action_desc TEXT;
BEGIN
    -- Get project name for the log message
    SELECT name INTO project_name FROM public.projects WHERE id = NEW.project_id;
    
    -- Only log on status changes
    IF TG_OP = 'UPDATE' AND OLD.status IS DISTINCT FROM NEW.status THEN
        -- Build descriptive action based on new status
        CASE NEW.status
            WHEN 'completed' THEN
                action_desc := 'Scan completed for ' || COALESCE(project_name, 'Unknown Project') || ' with score ' || COALESCE(NEW.score::TEXT, 'N/A');
            WHEN 'failed' THEN
                action_desc := 'Scan failed for ' || COALESCE(project_name, 'Unknown Project');
            WHEN 'scanning' THEN
                action_desc := 'Scan started for ' || COALESCE(project_name, 'Unknown Project');
            ELSE
                action_desc := 'Scan status changed to ' || NEW.status || ' for ' || COALESCE(project_name, 'Unknown Project');
        END CASE;
        
        -- Insert activity log
        INSERT INTO public.activity_logs (user_id, action_type, description, metadata, created_at)
        VALUES (
            NEW.initiated_by,
            CASE NEW.status
                WHEN 'completed' THEN 'scan_completed'
                WHEN 'failed' THEN 'scan_failed'
                WHEN 'scanning' THEN 'scan_started'
                ELSE 'scan_updated'
            END,
            action_desc,
            jsonb_build_object(
                'scan_id', NEW.id,
                'project_id', NEW.project_id,
                'project_name', project_name,
                'score', NEW.score,
                'status', NEW.status
            ),
            NOW()
        );
    ELSIF TG_OP = 'INSERT' THEN
        -- Log new scan creation
        action_desc := 'New scan queued for ' || COALESCE(project_name, 'Unknown Project');
        
        INSERT INTO public.activity_logs (user_id, action_type, description, metadata, created_at)
        VALUES (
            NEW.initiated_by,
            'scan_queued',
            action_desc,
            jsonb_build_object(
                'scan_id', NEW.id,
                'project_id', NEW.project_id,
                'project_name', project_name,
                'scan_type', NEW.type
            ),
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Drop existing trigger if exists (for idempotency)
DROP TRIGGER IF EXISTS on_scan_change ON public.scans;

-- 3. Create the trigger on scans table
CREATE TRIGGER on_scan_change
    AFTER INSERT OR UPDATE OF status ON public.scans
    FOR EACH ROW EXECUTE FUNCTION log_scan_activity();

-- 4. Create trigger for project creation logging
CREATE OR REPLACE FUNCTION log_project_activity()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.activity_logs (user_id, action_type, description, metadata, created_at)
    VALUES (
        NEW.user_id,
        'project_created',
        'Created project: ' || NEW.name,
        jsonb_build_object(
            'project_id', NEW.id,
            'project_name', NEW.name,
            'target_urls', NEW.target_urls
        ),
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_project_create ON public.projects;

CREATE TRIGGER on_project_create
    AFTER INSERT ON public.projects
    FOR EACH ROW EXECUTE FUNCTION log_project_activity();

-- 5. Ensure activity_logs table has proper RLS
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if present
DROP POLICY IF EXISTS "Users can view their own activity" ON public.activity_logs;

-- Create RLS policy for activity_logs
CREATE POLICY "Users can view their own activity"
    ON public.activity_logs
    FOR SELECT
    USING (auth.uid() = user_id);

-- =============================================================================
-- END OF MIGRATION
-- Run this in your Supabase SQL Editor
-- =============================================================================
