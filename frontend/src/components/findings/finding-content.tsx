'use client';

import React, { useState } from 'react';
import { FindingDetails } from '@/lib/api';

interface FindingContentProps {
  finding: FindingDetails;
  relatedFindings?: FindingDetails[];
}

export function FindingContent({ finding, relatedFindings = [] }: FindingContentProps) {
  const [activeTab, setActiveTab] = useState<'request' | 'response'>('request');

  const getSeverityColors = (s: string) => {
    switch (s) {
      case 'critical':
        return {
          text: 'text-rose-500',
          border: 'border-rose-500',
          bg: 'bg-rose-500/10',
          icon: 'text-rose-400',
        };
      case 'high':
        return {
          text: 'text-orange-500',
          border: 'border-orange-500',
          bg: 'bg-orange-500/10',
          icon: 'text-orange-400',
        };
      case 'medium':
        return {
          text: 'text-yellow-500',
          border: 'border-yellow-500',
          bg: 'bg-yellow-500/10',
          icon: 'text-yellow-400',
        };
      case 'low':
        return {
          text: 'text-blue-500',
          border: 'border-blue-500',
          bg: 'bg-blue-500/10',
          icon: 'text-blue-400',
        };
      default:
        return {
          text: 'text-slate-400',
          border: 'border-slate-500',
          bg: 'bg-slate-500/10',
          icon: 'text-slate-400',
        };
    }
  };

  const colors = getSeverityColors(finding.severity);

  // Parse evidence if it looks like JSON/HTTP, otherwise treating as text
  let requestContent =
    'POST /api/login HTTP/1.1\nHost: example.com\nContent-Type: application/json\n\n{\n  "username": "admin\' OR \'1\'=\'1",\n  "password": "password"\n}';
  let responseContent =
    'HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\n  "token": "ey..."\n}';

  // If evidence field exists, try to display it.
  // In a real scenario, we'd parse this robustly.
  if (finding.evidence) {
    if (finding.evidence.includes('HTTP')) {
      requestContent = finding.evidence;
    } else {
      requestContent = finding.evidence;
    }
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Details Section */}
      <section id="details" className="flex flex-col gap-4">
        <h3 className="text-xl font-bold text-white tracking-tight">Details</h3>
        <div
          className={`glass-panel rounded-xl p-5 bg-background/80 shadow-sm border ${colors.border} border-opacity-20`}
        >
          <details className="group" open>
            <summary className="flex cursor-pointer items-center justify-between font-medium text-gray-200 py-2 list-none hover:text-white transition-colors">
              <span>Vulnerability Description</span>
              <span className="material-symbols-outlined transition-transform group-open:rotate-180 text-gray-400">
                expand_more
              </span>
            </summary>
            <div className="mt-2 text-gray-400 leading-relaxed border-t border-white/5 pt-4">
              <p>{finding.description}</p>
              
              {/* Affected Locations List */}
               <div className="mt-6 pt-4 border-t border-white/5">
                <h4 className={`text-sm font-semibold ${colors.text} mb-3 flex items-center gap-2`}>
                   <span className="material-symbols-outlined text-sm">public</span>
                   Affected Locations ({relatedFindings.length > 0 ? relatedFindings.length : 1})
                </h4>
                
                {relatedFindings.length > 1 ? (
                  <div className="max-h-[300px] overflow-y-auto pr-2 custom-scrollbar space-y-2">
                     {relatedFindings.map((f, i) => (
                        <div key={i} className="flex items-center gap-2 bg-black/40 px-3 py-2 rounded border border-white/5 text-xs text-gray-300 font-mono break-all hover:bg-white/5 transition-colors">
                           <span className="text-slate-500 w-6 text-right">{i+1}.</span>
                           {f.location || 'Unknown Location'}
                        </div>
                     ))}
                  </div>
                ) : (
                   finding.location && (
                    <div className="bg-black/40 px-3 py-2 rounded border border-white/5 text-xs text-gray-300 font-mono break-all inline-block">
                       {finding.location}
                    </div>
                   )
                )}
              </div>

            </div>
          </details>
        </div>
      </section>

      {/* Evidence Section */}
      <section id="evidence" className="flex flex-col gap-4">
        <h3 className="text-xl font-bold text-white tracking-tight">Evidence</h3>

        {/* Request/Response Viewer */}
        <div
          className={`glass-panel rounded-xl overflow-hidden shadow-md border ${colors.border} border-opacity-20`}
        >
          <div className="flex border-b border-white/10 bg-black/40">
            <button
              onClick={() => setActiveTab('request')}
              className={`flex-1 py-3 text-sm font-bold border-b-2 transition-colors ${
                activeTab === 'request'
                  ? `${colors.border} text-white bg-white/5`
                  : 'border-transparent text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              HTTP Request
            </button>
            <button
              onClick={() => setActiveTab('response')}
              className={`flex-1 py-3 text-sm font-bold border-b-2 transition-colors ${
                activeTab === 'response'
                  ? `${colors.border} text-white bg-white/5`
                  : 'border-transparent text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              HTTP Response
            </button>
          </div>

          <div className="p-0 bg-[#0d1117] font-mono text-sm overflow-x-auto relative group">
            <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() =>
                  navigator.clipboard.writeText(
                    activeTab === 'request' ? requestContent : responseContent
                  )
                }
                className="p-1.5 rounded bg-white/10 hover:bg-white/20 text-white/70"
                title="Copy to clipboard"
              >
                <span className="material-symbols-outlined text-sm">content_copy</span>
              </button>
            </div>
            <pre className="p-4 text-gray-300 leading-relaxed whitespace-pre-wrap">
              {activeTab === 'request' ? (
                <code
                  dangerouslySetInnerHTML={{
                    // Simple highlighting for demo
                    __html: requestContent
                      .replace(
                        /(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)/g,
                        '<span class="text-rose-400">$1</span>'
                      )
                      .replace(/(HTTP\/1\.1)/g, '<span class="text-blue-400">$1</span>')
                      .replace(/([A-Za-z-]+:)/g, '<span class="text-cyan-400">$1</span>'),
                  }}
                />
              ) : (
                <code>{responseContent}</code>
              )}
            </pre>
          </div>
        </div>

        {/* Proof of Concept */}
        <div className={`glass-panel rounded-xl p-5 border-l-4 ${colors.border}`}>
          <p className="text-white font-medium mb-2 flex items-center gap-2">
            <span className={`material-symbols-outlined ${colors.icon}`}>science</span>
            Proof of Concept
          </p>
          <p className="text-gray-400 text-sm leading-relaxed">
            The vulnerability can be reproduced by sending the highlighted payload in the default
            tab. This demonstrates that the application logic fails to properly sanitize the input.
          </p>
        </div>
      </section>
    </div>
  );
}
