import { supabase } from './src/lib/supabase';

async function verifyJoin() {
  console.log('Verifying Scan -> Project Join...');

  // Fetch completed scans with projects
  const { data: scans, error } = await supabase
    .from('scans')
    .select(
      `
            id, status, project_id,
            projects (id, name, user_id)
        `
    )
    .eq('status', 'completed')
    .limit(5);

  if (error) {
    console.error('Error:', error);
    return;
  }

  if (!scans || scans.length === 0) {
    console.log('No joined scans found.');
  } else {
    console.table(
      scans.map((s) => ({
        id: s.id,
        status: s.status,
        projectName: Array.isArray(s.projects) ? s.projects[0]?.name : (s.projects as any)?.name,
        projectUser: Array.isArray(s.projects)
          ? s.projects[0]?.user_id
          : (s.projects as any)?.user_id,
      }))
    );
  }
}

verifyJoin();
