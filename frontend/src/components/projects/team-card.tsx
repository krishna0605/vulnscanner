'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { TeamMember } from '@/lib/api';
import { GlassCard } from './motion-wrapper';

export function TeamCard({ members }: { members: TeamMember[] }) {
  return (
    <GlassCard className="p-6 h-[350px] flex flex-col relative overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 z-10">
        <h3 className="text-white font-bold text-lg flex items-center gap-2">
          <span className="material-symbols-outlined text-cyan-400">groups</span>
          Team Active
        </h3>
        <Badge
          variant="outline"
          className="text-[10px] bg-emerald-500/10 text-emerald-500 border-emerald-500/20 animate-pulse"
        >
          {members.filter((m) => m.status !== 'offline').length} ONLINE
        </Badge>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 pr-4 -mr-4 z-10">
        <div className="space-y-4">
          {members.map((member) => (
            <div
              key={member.id}
              className="flex items-center justify-between group hover:bg-white/5 p-2 rounded-lg transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Avatar className="h-10 w-10 border border-white/10 group-hover:border-cyan-400/50 transition-colors">
                    <AvatarImage
                      src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${member.name}`}
                    />
                    <AvatarFallback className="bg-slate-800 text-white text-xs">
                      {member.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <span
                    className={`absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-slate-900 ${
                      member.status === 'online'
                        ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]'
                        : member.status === 'busy'
                          ? 'bg-amber-500'
                          : 'bg-slate-500'
                    }`}
                  ></span>
                </div>
                <div>
                  <p className="text-sm font-bold text-white leading-none group-hover:text-cyan-300 transition-colors">
                    {member.name}
                  </p>
                  <p className="text-[10px] text-slate-400 font-mono mt-1">{member.role}</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-500 font-medium">{member.lastActive}</span>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Background Blob */}
      <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-[50px] pointer-events-none"></div>
    </GlassCard>
  );
}
