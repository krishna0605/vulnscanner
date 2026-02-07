'use client';

import React, { useState } from 'react';
import { FindingDetails } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

interface FindingRemediationProps {
  finding: FindingDetails;
}

export function FindingRemediation({ finding }: FindingRemediationProps) {
  const [activeSection, setActiveSection] = useState<string>('details');
  const getSeverityColors = (s: string) => {
    switch (s) {
      case 'critical':
        return {
          text: 'text-rose-500',
          hover: 'hover:text-rose-400',
          border: 'border-rose-500/20',
          bg: 'bg-rose-500/10',
          marker: 'marker:text-rose-500',
          groupHover: 'group-hover:text-rose-400',
        };
      case 'high':
        return {
          text: 'text-orange-500',
          hover: 'hover:text-orange-400',
          border: 'border-orange-500/20',
          bg: 'bg-orange-500/10',
          marker: 'marker:text-orange-500',
          groupHover: 'group-hover:text-orange-400',
        };
      case 'medium':
        return {
          text: 'text-yellow-500',
          hover: 'hover:text-yellow-400',
          border: 'border-yellow-500/20',
          bg: 'bg-yellow-500/10',
          marker: 'marker:text-yellow-500',
          groupHover: 'group-hover:text-yellow-400',
        };
      case 'low':
        return {
          text: 'text-blue-500',
          hover: 'hover:text-blue-400',
          border: 'border-blue-500/20',
          bg: 'bg-blue-500/10',
          marker: 'marker:text-blue-500',
          groupHover: 'group-hover:text-blue-400',
        };
      default:
        return {
          text: 'text-slate-400',
          hover: 'hover:text-slate-300',
          border: 'border-slate-500/20',
          bg: 'bg-slate-500/10',
          marker: 'marker:text-slate-500',
          groupHover: 'group-hover:text-stone-400',
        };
    }
  };

  const colors = getSeverityColors(finding.severity);

  return (
    <div className="flex flex-col gap-6 sticky top-8">
      {/* Navigation */}
      <nav className="glass-nav rounded-lg flex flex-col p-2 space-y-1 bg-black/40 border border-white/10">
        <button
          onClick={() => {
            setActiveSection('details');
            document.getElementById('details')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
          className={`px-3 py-2 rounded-md text-sm font-medium transition-colors text-left ${
            activeSection === 'details'
              ? 'bg-white/10 text-white'
              : 'text-gray-400 hover:bg-white/10 hover:text-white'
          }`}
        >
          Details
        </button>
        <button
          onClick={() => {
            setActiveSection('evidence');
            document.getElementById('evidence')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
          className={`px-3 py-2 rounded-md text-sm font-medium transition-colors text-left ${
            activeSection === 'evidence'
              ? 'bg-white/10 text-white'
              : 'text-gray-400 hover:bg-white/10 hover:text-white'
          }`}
        >
          Evidence
        </button>
        <button
          onClick={() => {
            setActiveSection('remediation');
            document.getElementById('remediation')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
          className={`px-3 py-2 rounded-md text-sm font-medium ${colors.bg} ${colors.text} border ${colors.border} text-left shadow-sm`}
        >
          Remediation
        </button>
      </nav>

      {/* Remediation Steps */}
      <section id="remediation" className={`glass-panel rounded-xl p-5 border border-white/10`}>
        <h3 className="text-lg font-bold text-white mb-4">Remediation Steps</h3>
        {finding.remediation ? (
          <div className="prose prose-invert prose-sm max-w-none text-gray-300">
            <p className="whitespace-pre-line leading-relaxed">{finding.remediation}</p>
          </div>
        ) : (
          <ol
            className={`space-y-3 text-sm text-gray-300 list-decimal list-inside ${colors.marker}`}
          >
            <li>Validate all user inputs against a strict allowlist.</li>
            <li>Encode data before outputting to the browser.</li>
            <li>Keep libraries and frameworks up to date.</li>
          </ol>
        )}
      </section>

      {/* References */}
      <div className="glass-panel rounded-xl p-5 border-white/10">
        <h3 className="text-lg font-bold text-white mb-4">References</h3>
        <ul className="space-y-2">
          {finding.reference_links && finding.reference_links.length > 0 ? (
            finding.reference_links.map((link: string, idx: number) => (
              <li key={idx}>
                <a
                  href={link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-center gap-2 text-sm ${colors.text} ${colors.hover} hover:underline`}
                >
                  <span
                    className={`material-symbols-outlined text-base text-gray-500 ${colors.groupHover}`}
                  >
                    link
                  </span>
                  <span className="truncate">{link}</span>
                </a>
              </li>
            ))
          ) : (
            <>
              <li>
                <a
                  href="#"
                  className={`flex items-center gap-2 text-sm ${colors.text} ${colors.hover} hover:underline group`}
                >
                  <span
                    className={`material-symbols-outlined text-base text-gray-500 ${colors.groupHover} transition-colors`}
                  >
                    link
                  </span>
                  OWASP Top 10
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className={`flex items-center gap-2 text-sm ${colors.text} ${colors.hover} hover:underline group`}
                >
                  <span
                    className={`material-symbols-outlined text-base text-gray-500 ${colors.groupHover} transition-colors`}
                  >
                    link
                  </span>
                  Common Weakness Enumeration
                </a>
              </li>
            </>
          )}
        </ul>
      </div>

      {/* Metadata */}
      <div className="glass-panel rounded-xl p-5 border-white/10">
        <h3 className="text-lg font-bold text-white mb-4">Finding Details</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Discovered On</span>
            <span className="font-medium text-gray-200">
              {new Date(finding.created_at).toLocaleDateString()}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Scanner</span>
            <span className="font-medium text-gray-200">VulnScanner Bot</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Age</span>
            <span className="font-medium text-gray-200">
              {formatDistanceToNow(new Date(finding.created_at))} ago
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
