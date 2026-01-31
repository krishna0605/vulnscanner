import { ProjectForm } from '@/components/projects/project-form';
import { getProject } from '@/app/actions';
import { redirect } from 'next/navigation';

export const dynamic = 'force-dynamic';

interface PageProps {
  params: {
    id: string;
  };
}

export default async function EditProjectPage({ params }: PageProps) {
  const project = await getProject(params.id);

  if (!project) {
    redirect('/projects');
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-white">Edit Project</h1>
        <p className="text-slate-400">Update project details and scope.</p>
      </div>

      <ProjectForm initialData={project} />
    </div>
  );
}
