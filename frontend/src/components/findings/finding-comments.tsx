'use client';

import React, { useState, useEffect } from 'react';
import { FindingComment, getFindingComments, addFindingComment } from '@/app/actions';
import { formatDistanceToNow } from 'date-fns';

interface FindingCommentsProps {
  findingId: string;
  severity: string;
}

export function FindingComments({ findingId, severity }: FindingCommentsProps) {
  const [comments, setComments] = useState<FindingComment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Dynamic styles based on severity (using same logic as Header/Stats)
  const getSeverityColors = (s: string) => {
    switch (s) {
      case 'critical':
        return { button: 'bg-rose-600 hover:bg-rose-500', ring: 'focus:ring-rose-500' };
      case 'high':
        return { button: 'bg-orange-600 hover:bg-orange-500', ring: 'focus:ring-orange-500' };
      case 'medium':
        return { button: 'bg-yellow-600 hover:bg-yellow-500', ring: 'focus:ring-yellow-500' };
      case 'low':
        return { button: 'bg-blue-600 hover:bg-blue-500', ring: 'focus:ring-blue-500' };
      default:
        return { button: 'bg-slate-600 hover:bg-slate-500', ring: 'focus:ring-slate-500' };
    }
  };
  const colors = getSeverityColors(severity);

  useEffect(() => {
    loadComments();
  }, [findingId]);

  const loadComments = async () => {
    setLoading(true);
    const data = await getFindingComments(findingId);
    setComments(data);
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmitting(true);
    const result = await addFindingComment(findingId, newComment);
    if (result) {
      setComments([result, ...comments]);
      setNewComment('');
    }
    setSubmitting(false);
  };

  return (
    <div className="glass-panel rounded-xl p-6 border border-white/10 mt-8">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="material-symbols-outlined text-gray-400">forum</span>
        Team Discussion
      </h3>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="relative">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment or note..."
            className={`w-full bg-black/20 border border-white/10 rounded-lg p-4 text-gray-200 placeholder:text-gray-500 focus:outline-none focus:ring-1 ${colors.ring} min-h-[100px] resize-y transition-all`}
          />
          <div className="absolute bottom-3 right-3">
            <button
              type="submit"
              disabled={submitting || !newComment.trim()}
              className={`${colors.button} text-white px-4 py-1.5 rounded-md text-sm font-bold shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {submitting ? 'Posting...' : 'Post Comment'}
            </button>
          </div>
        </div>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2].map((i) => (
            <div key={i} className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-white/5"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-white/5 w-1/4 rounded"></div>
                <div className="h-4 bg-white/5 w-3/4 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      ) : comments.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-50">
            chat_bubble_outline
          </span>
          <p>No comments yet. Start the discussion!</p>
        </div>
      ) : (
        <div className="space-y-6">
          {comments.map((comment) => (
            <div key={comment.id} className="flex gap-4 group">
              {/* Avatar Placeholder */}
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center border border-white/10 text-xs font-bold text-gray-300">
                {comment.user_email.substring(0, 2).toUpperCase()}
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-gray-200 text-sm">{comment.user_email}</span>
                  <span className="text-xs text-gray-500">
                    {formatDistanceToNow(new Date(comment.created_at))} ago
                  </span>
                </div>
                <div className="text-gray-400 text-sm leading-relaxed whitespace-pre-wrap bg-white/[0.02] p-3 rounded-lg border border-transparent group-hover:border-white/5 transition-colors">
                  {comment.content}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
