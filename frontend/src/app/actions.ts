'use server';

import { revalidatePath } from 'next/cache';
import { api } from '@convex/_generated/api';
import type { Id } from '@convex/_generated/dataModel';
import { getConvexServerClient } from '@/lib/convex-server';
import { logger } from '@/utils/logger';

export interface FindingComment {
  id: string;
  content: string;
  created_at: string;
  user_email: string;
}

export async function getFindingComments(findingId: string): Promise<FindingComment[]> {
  const client = await getConvexServerClient();
  return await client.query(api.comments.list, {
    findingId: findingId as Id<'findings'>,
  });
}

export async function addFindingComment(
  findingId: string,
  content: string
): Promise<FindingComment | null> {
  const client = await getConvexServerClient();
  try {
    return await client.mutation(api.comments.add, {
      findingId: findingId as Id<'findings'>,
      content,
    });
  } catch (error) {
    logger.error(`Error adding comment for ${findingId}:`, { error });
    return null;
  }
}

export async function updateFindingStatus(
  findingId: string,
  status: 'open' | 'fixed' | 'false_positive'
): Promise<{ success: boolean; error?: string }> {
  const client = await getConvexServerClient();
  try {
    await client.mutation(api.findings.updateStatus, {
      findingId: findingId as Id<'findings'>,
      status,
    });
    revalidatePath('/reports');
    return { success: true };
  } catch (error: any) {
    logger.error(`Error updating finding status for ${findingId}:`, { error });
    return { success: false, error: error?.message ?? 'Failed to update finding status' };
  }
}

export async function saveIntegrationConfig(
  projectId: string,
  type: 'jira' | 'github',
  config: any
) {
  if (!projectId) {
    throw new Error('Failed to save configuration: Project ID is missing');
  }

  const client = await getConvexServerClient();
  return await client.mutation(api.integrations.upsert, {
    projectId: projectId as Id<'projects'>,
    type,
    config,
  });
}

export async function getIntegrationConfig(projectId: string, type: 'jira' | 'github') {
  const client = await getConvexServerClient();
  const integration = await client.query(api.integrations.get, {
    projectId: projectId as Id<'projects'>,
    type,
  });
  return integration?.config ?? null;
}

export async function createIssue(
  finding: any,
  integrationType: 'jira' | 'github',
  projectId: string
) {
  const config = await getIntegrationConfig(projectId, integrationType);
  if (!config) throw new Error(`No configuration found for ${integrationType}`);

  try {
    if (integrationType === 'jira') {
      const auth = Buffer.from(`${config.email}:${config.token}`).toString('base64');
      const res = await fetch(`${config.url}/rest/api/3/issue`, {
        method: 'POST',
        headers: {
          Authorization: `Basic ${auth}`,
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fields: {
            project: { key: config.project_key },
            summary: `[VulnScanner] ${finding.title}`,
            description: {
              type: 'doc',
              version: 1,
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: finding.description ?? finding.evidence ?? '' }],
                },
                {
                  type: 'paragraph',
                  content: [
                    {
                      type: 'text',
                      text: `Severity: ${finding.severity?.toUpperCase?.() ?? finding.severity}\nStatus: ${finding.status}`,
                    },
                  ],
                },
              ],
            },
            issuetype: { name: 'Bug' },
          },
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Failed to create Jira issue: ${res.status} - ${errText}`);
      }

      const json = await res.json();
      return { url: `${config.url}/browse/${json.key}`, key: json.key };
    }

    const res = await fetch(`https://api.github.com/repos/${config.owner}/${config.repo}/issues`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.token}`,
        Accept: 'application/vnd.github.v3+json',
        'User-Agent': 'VulnScanner-App',
      },
      body: JSON.stringify({
        title: `[Vuln] ${finding.title}`,
        body: `**Description**\n${finding.description ?? finding.evidence ?? ''}\n\n**Severity:** ${finding.severity}\n**Status:** ${finding.status}\n\n*Reported by VulnScanner*`,
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Failed to create GitHub issue: ${res.status} - ${errText}`);
    }

    const json = await res.json();
    return { url: json.html_url, key: `#${json.number}` };
  } catch (error: any) {
    logger.error('Integration Error:', { error });
    throw new Error(error?.message || 'External API call failed');
  }
}

export async function createProject(formData: FormData) {
  const client = await getConvexServerClient();
  const name = String(formData.get('name') ?? '').trim();
  const description = String(formData.get('description') ?? '').trim();
  const targetUrls = parseTargetUrls(formData.get('targets'));

  if (!name) {
    throw new Error('Project name is required');
  }

  const project = await client.mutation(api.projects.create, {
    name,
    description: description || undefined,
    targetUrls,
  });

  revalidatePath('/projects');
  return project;
}

export async function updateProject(projectId: string, formData: FormData) {
  const client = await getConvexServerClient();
  const name = String(formData.get('name') ?? '').trim();
  const description = String(formData.get('description') ?? '').trim();
  const targetUrls = parseTargetUrls(formData.get('targets'));

  if (!name) {
    throw new Error('Project name is required');
  }

  const project = await client.mutation(api.projects.update, {
    projectId: projectId as Id<'projects'>,
    name,
    description: description || undefined,
    targetUrls,
  });

  revalidatePath('/projects');
  revalidatePath(`/projects/${projectId}`);
  return project;
}

export async function deleteProject(projectId: string) {
  const client = await getConvexServerClient();
  await client.mutation(api.projects.remove, { projectId: projectId as Id<'projects'> });
  revalidatePath('/projects');
}

export async function startProjectScan(projectId: string) {
  const client = await getConvexServerClient();
  const project = await client.query(api.projects.get, { projectId: projectId as Id<'projects'> });
  if (!project) {
    throw new Error('Project not found');
  }

  const targetUrl =
    project.target_urls?.[0] ?? project.targetUrls?.[0] ?? project.targets?.[0] ?? 'https://example.com';

  const scan = await client.action(api.scans.start, {
    projectId: projectId as Id<'projects'>,
    targetUrl,
    type: 'full',
    config: { scanType: 'full', source: 'project_table' },
  });

  revalidatePath('/scans');
  return scan;
}

export async function getProject(projectId: string) {
  const client = await getConvexServerClient();
  return await client.query(api.projects.get, { projectId: projectId as Id<'projects'> });
}

function parseTargetUrls(rawTargets: FormDataEntryValue | null) {
  if (!rawTargets || typeof rawTargets !== 'string') {
    return [];
  }

  try {
    const targets = JSON.parse(rawTargets);
    if (!Array.isArray(targets)) return [];
    return targets.map((target) => String(target?.value ?? '').trim()).filter(Boolean);
  } catch (error) {
    logger.error('Failed to parse project targets', { error });
    return [];
  }
}
