'use server';

import { createClient } from '@/utils/supabase/server';
import { logger } from '@/utils/logger';

export interface FindingComment {
  id: string;
  content: string;
  created_at: string;
  user_email: string;
}

export async function getFindingComments(findingId: string): Promise<FindingComment[]> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc('get_finding_comments', { finding_uuid: findingId });

  if (error) {
    logger.error(`Error fetching comments for ${findingId}:`, { error });
    return [];
  }

  return data as FindingComment[];
}

export async function addFindingComment(
  findingId: string,
  content: string
): Promise<FindingComment | null> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc('add_finding_comment', {
    finding_uuid: findingId,
    comment_content: content,
  });

  if (error) {
    logger.error(`Error adding comment for ${findingId}:`, { error });
    return null;
  }

  // RPC returns a single object
  return data as FindingComment;
}

// -- Integrations --

// -- Finding Status --

export async function updateFindingStatus(
  findingId: string,
  status: 'open' | 'fixed' | 'false_positive'
): Promise<{ success: boolean; error?: string }> {
  const supabase = createClient();

  const { error } = await supabase
    .from('findings')
    .update({ status })
    .eq('id', findingId);

  if (error) {
    logger.error(`Error updating finding status for ${findingId}:`, { error });
    return { success: false, error: error.message };
  }

  return { success: true };
}

// -- Integration Config --


export async function saveIntegrationConfig(
  projectId: string,
  type: 'jira' | 'github',
  config: any
) {
  logger.info('saveIntegrationConfig called:', { projectId, type, configKeys: Object.keys(config || {}) });
  
  if (!projectId) {
    logger.error('saveIntegrationConfig: projectId is missing or undefined');
    throw new Error('Failed to save configuration: Project ID is missing');
  }
  
  const supabase = createClient();
  const { data, error } = await supabase.rpc('upsert_integration', {
    p_project_id: projectId,
    p_type: type,
    p_config: config,
  });

  if (error) {
    logger.error('Error saving integration:', { 
      error, 
      errorCode: error.code,
      errorMessage: error.message,
      errorDetails: error.details,
      projectId,
      type 
    });
    throw new Error(`Failed to save configuration: ${error.message}`);
  }
  
  logger.info('Integration config saved successfully:', { data });
  return data;
}

export async function getIntegrationConfig(projectId: string, type: 'jira' | 'github') {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('integrations')
    .select('config')
    .eq('project_id', projectId)
    .eq('type', type)
    .single();

  if (error) return null;
  return data?.config;
}

export async function createIssue(
  finding: any,
  integrationType: 'jira' | 'github',
  projectId: string
) {
  // 1. Get Config
  const config = await getIntegrationConfig(projectId, integrationType);
  if (!config) throw new Error(`No configuration found for ${integrationType}`);

  // 2. Call External API
  // NOTE: In a real app, we would decrypt the token here if it was encrypted.

  try {
    if (integrationType === 'jira') {
      // Jira Cloud REST API v3
      // Auth: Basic (Email : API Token) encoded in base64
      const auth = Buffer.from(`${config.email}:${config.token}`).toString('base64');

      const body = {
        fields: {
          project: { key: config.project_key },
          summary: `[VulnScanner] ${finding.title}`,
          description: {
            type: 'doc',
            version: 1,
            content: [
              {
                type: 'paragraph',
                content: [{ type: 'text', text: finding.description }],
              },
              {
                type: 'paragraph',
                content: [
                  {
                    type: 'text',
                    text: `Severity: ${finding.severity.toUpperCase()}\nStatus: ${finding.status}`,
                  },
                ],
              },
            ],
          },
          issuetype: { name: 'Bug' },
        },
      };

      const res = await fetch(`${config.url}/rest/api/3/issue`, {
        method: 'POST',
        headers: {
          Authorization: `Basic ${auth}`,
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errText = await res.text();
        logger.error('Jira API Error:', { error: errText });
        throw new Error('Failed to create Jira issue: ' + res.statusText);
      }

      const json = await res.json();
      return { url: `${config.url}/browse/${json.key}`, key: json.key };
    } else if (integrationType === 'github') {
      // GitHub REST API
      // POST /repos/{owner}/{repo}/issues
      const res = await fetch(
        `https://api.github.com/repos/${config.owner}/${config.repo}/issues`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${config.token}`,
            Accept: 'application/vnd.github.v3+json',
            'User-Agent': 'VulnScanner-App',
          },
          body: JSON.stringify({
            title: `[Vuln] ${finding.title}`,
            body: `**Description**\n${finding.description}\n\n**Severity:** ${finding.severity}\n**Status:** ${finding.status}\n\n*Reported by VulnScanner*`,
          }),
        }
      );

      if (!res.ok) {
        const errText = await res.text();
        logger.error('GitHub API Error:', { 
          status: res.status, 
          statusText: res.statusText,
          error: errText,
          owner: config.owner,
          repo: config.repo 
        });
        throw new Error(`Failed to create GitHub issue: ${res.status} - ${errText}`);
      }

      const json = await res.json();
      return { url: json.html_url, key: `#${json.number}` };
    }
  } catch (e: any) {
    logger.error('Integration Error:', { error: e });
    throw new Error(e.message || 'External API call failed');
  }
}
// -- Projects --

export async function createProject(formData: FormData) {
  const supabase = createClient();

  // 1. Get User
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error('Unauthorized');

  // 2. Extract Data
  const name = formData.get('name') as string;
  const description = formData.get('description') as string;
  const department = formData.get('department') as string;

  // 3. Insert
  const { data, error } = await supabase
    .from('projects')
    .insert({
      name,
      description,
      user_id: user.id,
      // We could store department in metadata or a new column if needed
    })
    .select()
    .single();

  if (error) {
    logger.error('Create Project Error:', { error });
    throw new Error('Failed to create project');
  }

  // 4. Handle Targets (Assets) and update target_urls array
  const targetsJson = formData.get('targets') as string;
  if (targetsJson) {
    try {
      const targets = JSON.parse(targetsJson);
      const targetUrls = targets.map((t: any) => t.value).filter(Boolean);

      // Update project with target_urls array
      if (targetUrls.length > 0) {
        await supabase
          .from('projects')
          .update({
            target_urls: targetUrls,
            updated_at: new Date().toISOString(),
          })
          .eq('id', data.id);
      }

      // Also create assets for each target
      const assets = targets
        .map((t: any) => ({
          project_id: data.id,
          url: t.value,
          type: 'page',
        }))
        .filter((a: any) => a.url);

      if (assets.length > 0) {
        await supabase.from('assets').insert(assets);
      }
    } catch (e) {
      logger.error('Failed to parse targets', { error: e });
    }
  }

  return data;
}

export async function deleteProject(projectId: string) {
  const supabase = createClient();
  const { error } = await supabase.from('projects').delete().eq('id', projectId);

  if (error) {
    logger.error('Delete Project Error:', { error });
    throw new Error('Failed to delete project');
  }
}

export async function startProjectScan(projectId: string) {
  const supabase = createClient();

  // 1. Get Project to find target URL (simplified: just picking first asset or project description/metadata if available)
  // In a real app, you might scan ALL assets or a specific one.
  // For now, we'll look for an Asset or just use a placeholder based on project name if Assets table is empty/complex.
  const { data: assets } = await supabase
    .from('assets')
    .select('url')
    .eq('project_id', projectId)
    .limit(1);

  const targetUrl = assets && assets.length > 0 ? assets[0].url : 'https://example.com'; // Fallback

  // 2. Create Scan
  const { data, error } = await supabase
    .from('scans')
    .insert({
      project_id: projectId,
      target_url: targetUrl,
      status: 'queued',
      type: 'full',
      progress: 0,
      current_action: 'Initializing...',
    })
    .select()
    .single();

  if (error) {
    logger.error('Start Scan Error:', { error });
    throw new Error('Failed to start scan');
  }

  return data;
}

export async function getProject(projectId: string) {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('projects')
    .select(
      `
            *,
            assets (*)
        `
    )
    .eq('id', projectId)
    .single();

  if (error) return null;
  return data;
}

export async function updateProject(projectId: string, formData: FormData) {
  const supabase = createClient();

  const name = formData.get('name') as string;
  const description = formData.get('description') as string;
  const department = formData.get('department') as string;

  // 1. Update Project Details
  const { error: updateError } = await supabase
    .from('projects')
    .update({
      name,
      description,
      // department can be stored in metadata if needed
    })
    .eq('id', projectId);

  if (updateError) {
    logger.error('Update Project Error:', { error: updateError });
    throw new Error('Failed to update project');
  }

  // Check if targets were sent
  const targetsJson = formData.get('targets') as string;
  if (targetsJson) {
    try {
      const targets = JSON.parse(targetsJson);
      // Simplified asset handling: just add new ones for now
      const assets = targets
        .map((t: any) => ({
          project_id: projectId,
          url: t.value,
          type: 'page',
        }))
        .filter((a: any) => a.url);

      if (assets.length > 0) {
        // Logic to handle assets during edit (e.g. upsert) can go here
      }
    } catch (e) {
      logger.error('Failed to parse targets', { error: e });
    }
  }
}
