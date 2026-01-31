'use client';

import React from 'react';
import { FindingDetails } from '@/lib/api';

interface FindingStatsProps {
  finding: FindingDetails;
}

export function FindingStats({ finding }: FindingStatsProps) {
  const getSeverityColors = (s: string) => {
    switch (s) {
      case 'critical':
        return {
          text: 'text-rose-500',
          hover: 'hover:text-rose-400',
          border: 'border-rose-500/20',
          bg: 'bg-rose-500/10',
        };
      case 'high':
        return {
          text: 'text-orange-500',
          hover: 'hover:text-orange-400',
          border: 'border-orange-500/20',
          bg: 'bg-orange-500/10',
        };
      case 'medium':
        return {
          text: 'text-yellow-500',
          hover: 'hover:text-yellow-400',
          border: 'border-yellow-500/20',
          bg: 'bg-yellow-500/10',
        };
      case 'low':
        return {
          text: 'text-blue-500',
          hover: 'hover:text-blue-400',
          border: 'border-blue-500/20',
          bg: 'bg-blue-500/10',
        };
      default:
        return {
          text: 'text-slate-400',
          hover: 'hover:text-slate-300',
          border: 'border-slate-500/20',
          bg: 'bg-slate-500/10',
        };
    }
  };

  const colors = getSeverityColors(finding.severity);

  return (
    <div
      className={`glass-panel rounded-xl p-6 hover:shadow-lg transition-all duration-300 border ${colors.border}`}
    >
      <h3 className="text-lg font-bold text-white mb-6">Quick Stats</h3>

      <div className="space-y-6">
        {/* CVSS Score */}
        <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg">
          <span className="text-gray-300 font-medium">CVSS Score</span>
          <span className={`text-2xl font-black ${colors.text}`}>
            {finding.cvss_score?.toFixed(1) || <span className="text-gray-500 text-lg">N/A</span>}
          </span>
        </div>

        {/* CVE */}
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-gray-400">CVE</span>
          {finding.cve_id ? (
            <a
              href={`https://nvd.nist.gov/vuln/detail/${finding.cve_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className={`font-mono ${colors.text} ${colors.hover} hover:underline transition-colors`}
            >
              {finding.cve_id}
            </a>
          ) : (
            <span className="text-gray-600 font-mono">N/A</span>
          )}
        </div>

        {/* CWE */}
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-gray-400">CWE</span>
          {finding.cwe_id ? (
            <a
              href={`https://cwe.mitre.org/data/definitions/${finding.cwe_id.replace('CWE-', '')}.html`}
              target="_blank"
              rel="noopener noreferrer"
              className={`font-mono ${colors.text} ${colors.hover} hover:underline transition-colors`}
            >
              {finding.cwe_id}
            </a>
          ) : (
            <span className="text-gray-600 font-mono">N/A</span>
          )}
        </div>
      </div>
    </div>
  );
}
