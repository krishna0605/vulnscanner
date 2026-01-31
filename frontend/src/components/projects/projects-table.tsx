'use client';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Play, PenLine, Trash2, FileText } from 'lucide-react';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MoreHorizontal } from 'lucide-react';
import { ProjectTableRow } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { useRouter } from 'next/navigation';
import { deleteProject, startProjectScan } from '@/app/actions';
import { useTransition } from 'react';
import { EmptyState } from '@/components/ui/empty-state';

interface ProjectsTableProps {
  data: ProjectTableRow[];
}

export function ProjectsTable({ data }: ProjectsTableProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    startTransition(async () => {
      try {
        await deleteProject(id);
        router.refresh();
      } catch (e) {
        alert('Failed to delete project');
      }
    });
  };

  const handleStartScan = async (id: string) => {
    startTransition(async () => {
      try {
        await startProjectScan(id);
        alert('Scan started successfully! Check Active Scans.');
        router.refresh();
      } catch (e) {
        alert('Failed to start scan');
      }
    });
  };

  return (
    <Table>
      <TableHeader className="bg-white/5">
        <TableRow className="hover:bg-transparent border-white/5">
          <TableHead className="text-[11px] uppercase tracking-wider text-slate-400 font-mono pl-6">
            Project
          </TableHead>
          <TableHead className="text-[11px] uppercase tracking-wider text-slate-400 font-mono">
            Status
          </TableHead>
          <TableHead className="text-[11px] uppercase tracking-wider text-slate-400 font-mono">
            Last Scan
          </TableHead>
          <TableHead className="text-right text-[11px] uppercase tracking-wider text-slate-400 font-mono pr-6">
            Actions
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((project) => (
          <TableRow
            key={project.id}
            className="group hover:bg-white/[0.02] border-white/5 transition-colors"
          >
            <TableCell className="font-medium pl-6">
              <div className="flex flex-col">
                <span
                  onClick={() => router.push(`/projects/${project.id}`)}
                  className="text-white font-semibold text-sm group-hover:text-cyan-400 transition-colors cursor-pointer"
                >
                  {project.name}
                </span>
                <span className="text-xs text-slate-500 truncate max-w-[200px]">
                  {project.description || 'No description provided'}
                </span>
              </div>
            </TableCell>
            <TableCell>
              <Badge
                variant={
                  project.status === 'active'
                    ? 'default'
                    : project.status === 'archived'
                      ? 'secondary'
                      : 'outline'
                }
                className={`uppercase text-[10px] tracking-widest font-bold ${
                  project.status === 'active'
                    ? 'bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]'
                    : project.status === 'pending'
                      ? 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20'
                      : 'bg-slate-500/10 text-slate-400'
                }`}
              >
                {project.status}
              </Badge>
            </TableCell>
            <TableCell>
              <span className="text-slate-400 text-xs font-mono">
                {formatDistanceToNow(new Date(project.lastScan || new Date()), { addSuffix: true })}
              </span>
            </TableCell>
            <TableCell className="text-right pr-6">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-slate-400 hover:text-white hover:bg-white/10 rounded-full"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="bg-[#1a1a1a] border-white/10 text-slate-300 w-48"
                >
                  <DropdownMenuLabel className="text-xs uppercase tracking-wider text-slate-500 font-mono">
                    Actions
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator className="bg-white/10" />

                  <DropdownMenuItem
                    disabled={isPending}
                    onClick={() => handleStartScan(project.id)}
                    className="text-xs font-medium focus:bg-cyan-500/10 focus:text-cyan-400 cursor-pointer"
                  >
                    <Play className="h-3.5 w-3.5 mr-2" />
                    Start Scan
                  </DropdownMenuItem>

                  <DropdownMenuItem
                    onClick={() => router.push(`/reports?project=${project.id}`)}
                    className="text-xs font-medium focus:bg-white/5 focus:text-white cursor-pointer"
                  >
                    <FileText className="h-3.5 w-3.5 mr-2" />
                    View Reports
                  </DropdownMenuItem>

                  <DropdownMenuItem
                    onClick={() => router.push(`/projects/${project.id}/edit`)}
                    className="text-xs font-medium focus:bg-white/5 focus:text-white cursor-pointer"
                  >
                    <PenLine className="h-3.5 w-3.5 mr-2" />
                    Edit Project
                  </DropdownMenuItem>

                  <DropdownMenuSeparator className="bg-white/10" />

                  <DropdownMenuItem
                    disabled={isPending}
                    onClick={() => handleDelete(project.id)}
                    className="text-xs font-medium text-red-400 focus:bg-red-500/10 focus:text-red-300 cursor-pointer"
                  >
                    <Trash2 className="h-3.5 w-3.5 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
        {(!data || data.length === 0) && (
          <TableRow>
            <TableCell colSpan={4} className="h-64 text-center">
              <EmptyState
                icon="layers_clear"
                title="No Projects Found"
                message="Create a new project to start scanning."
                className="border-none bg-transparent h-full"
              />
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
