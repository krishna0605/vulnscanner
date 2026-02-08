'use client';

import React from 'react';
import Link from 'next/link';
import { FindingDetails } from '@/lib/api';

interface FindingHeaderProps {
  finding: FindingDetails;
}

import { generateFindingPDF } from '@/utils/pdf-generator';
import { useState } from 'react';
import { createIssue, saveIntegrationConfig, updateFindingStatus } from '@/app/actions';
import { logger } from '@/utils/logger';

export function FindingHeader({ finding }: FindingHeaderProps) {
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  // Integration State
  const [showIntegrationModal, setShowIntegrationModal] = useState(false);
  const [integrationType, setIntegrationType] = useState<'jira' | 'github'>('github');
  const [config, setConfig] = useState({
    url: '',
    email: '',
    token: '',
    project_key: '',
    owner: '',
    repo: '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [isCreatingTicket, setIsCreatingTicket] = useState(false);
  const [ticketUrl, setTicketUrl] = useState<string | null>(null);

  // Mark as Resolved State
  const [isMarkingResolved, setIsMarkingResolved] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(finding.status);
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);

  const handleDownloadPdf = async () => {
    setIsGeneratingPdf(true);
    await generateFindingPDF(finding);
    setIsGeneratingPdf(false);
  };

  const handleCreateTicket = async () => {
    setIsCreatingTicket(true);
    try {
      const result = await createIssue(finding, integrationType, finding.project_id);
      if (result) {
        setTicketUrl(result.url);
        alert(`Ticket created successfully! ${result.key}`);
      }
    } catch (e) {
      logger.error('Error creating ticket:', { error: e });
      // If failed, likely no config, show config modal
      if (confirm('Integration not configured or failed. Configure now?')) {
        setShowIntegrationModal(true);
      }
    } finally {
      setIsCreatingTicket(false);
    }
  };

  const handleSaveConfig = async () => {
    setIsSaving(true);
    try {
      // Filter config based on type
      const cleanConfig =
        integrationType === 'jira'
          ? {
              url: config.url,
              email: config.email,
              token: config.token,
              project_key: config.project_key,
            }
          : { owner: config.owner, repo: config.repo, token: config.token };

      await saveIntegrationConfig(finding.project_id, integrationType, cleanConfig);
      alert('Configuration saved!');
      setShowIntegrationModal(false);
    } catch (e) {
      alert('Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleMarkAsResolved = async (newStatus: 'fixed' | 'false_positive') => {
    setIsMarkingResolved(true);
    setShowStatusDropdown(false);
    try {
      const result = await updateFindingStatus(finding.id, newStatus);
      if (result.success) {
        setCurrentStatus(newStatus);
      } else {
        alert('Failed to update status: ' + result.error);
      }
    } catch (e) {
      logger.error('Error marking as resolved:', { error: e });
      alert('Failed to update status');
    } finally {
      setIsMarkingResolved(false);
    }
  };

  const handleReopenFinding = async () => {
    setIsMarkingResolved(true);
    try {
      const result = await updateFindingStatus(finding.id, 'open');
      if (result.success) {
        setCurrentStatus('open');
      } else {
        alert('Failed to reopen: ' + result.error);
      }
    } catch (e) {
      logger.error('Error reopening finding:', { error: e });
      alert('Failed to reopen finding');
    } finally {
      setIsMarkingResolved(false);
    }
  };

  const getSeverityColors = (s: string) => {
    switch (s) {
      case 'critical':
        return {
          text: 'text-rose-500',
          hover: 'hover:text-rose-400',
          border: 'border-rose-500/20',
          bg: 'bg-rose-500/10',
          button: 'bg-rose-600 hover:bg-rose-500 shadow-rose-900/20',
        };
      case 'high':
        return {
          text: 'text-orange-500',
          hover: 'hover:text-orange-400',
          border: 'border-orange-500/20',
          bg: 'bg-orange-500/10',
          button: 'bg-orange-600 hover:bg-orange-500 shadow-orange-900/20',
        };
      case 'medium':
        return {
          text: 'text-yellow-500',
          hover: 'hover:text-yellow-400',
          border: 'border-yellow-500/20',
          bg: 'bg-yellow-500/10',
          button: 'bg-yellow-600 hover:bg-yellow-500 shadow-yellow-900/20',
        };
      case 'low':
        return {
          text: 'text-blue-500',
          hover: 'hover:text-blue-400',
          border: 'border-blue-500/20',
          bg: 'bg-blue-500/10',
          button: 'bg-blue-600 hover:bg-blue-500 shadow-blue-900/20',
        };
      default:
        return {
          text: 'text-slate-400',
          hover: 'hover:text-slate-300',
          border: 'border-slate-500/20',
          bg: 'bg-slate-500/10',
          button: 'bg-slate-600 hover:bg-slate-500 shadow-slate-900/20',
        };
    }
  };

  const colors = getSeverityColors(finding.severity);

  return (
    <header className="mb-8">
      {/* Breadcrumbs Removed as per user request */}

      {/* Title & Actions */}
      <div className="flex flex-wrap justify-between gap-4 items-end">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl md:text-4xl font-black tracking-tight text-white">
            {finding.title}
          </h1>
          <span
            className={`
            px-3 py-1 text-sm font-bold rounded-full border items-center inline-flex
            ${finding.severity === 'critical' ? 'bg-red-500/10 border-red-500/20 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.4)]' : ''}
            ${finding.severity === 'high' ? 'bg-orange-500/10 border-orange-500/20 text-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.3)]' : ''}
            ${finding.severity === 'medium' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500' : ''}
            ${finding.severity === 'low' ? 'bg-blue-500/10 border-blue-500/20 text-blue-500' : ''}
            ${finding.severity === 'info' ? 'bg-gray-500/10 border-gray-500/20 text-gray-400' : ''}
          `}
          >
            {finding.severity.toUpperCase()}
          </span>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleDownloadPdf}
            disabled={isGeneratingPdf}
            className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white px-5 py-2.5 rounded-lg font-bold transition-all border border-white/10 disabled:opacity-50 disabled:cursor-wait"
          >
            <span className="material-symbols-outlined text-xl">
              {isGeneratingPdf ? 'progress_activity' : 'picture_as_pdf'}
            </span>
            <span>{isGeneratingPdf ? 'Generating...' : 'Export PDF'}</span>
          </button>

          <div className="relative group">
            <button
              onClick={handleCreateTicket}
              disabled={isCreatingTicket}
              className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white px-5 py-2.5 rounded-lg font-bold transition-all border border-white/10 disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-xl">bug_report</span>
              <span>{isCreatingTicket ? 'Creating...' : 'Create Ticket'}</span>
            </button>
            {/* Quick Config Trigger (Hover/Click to configure if needed - simplified to just a small gear for now) */}
            <button
              onClick={() => setShowIntegrationModal(true)}
              className="absolute -top-2 -right-2 bg-gray-800 text-gray-400 p-1 rounded-full text-xs hover:text-white"
              title="Configure Integration"
            >
              <span className="material-symbols-outlined text-sm">settings</span>
            </button>
          </div>

          {/* Mark as Resolved / Status Button */}
          <div className="relative">
            {currentStatus === 'open' ? (
              <>
                <button
                  onClick={() => setShowStatusDropdown(!showStatusDropdown)}
                  disabled={isMarkingResolved}
                  className={`flex items-center gap-2 ${colors.button} text-white px-5 py-2.5 rounded-lg font-bold transition-all shadow-lg disabled:opacity-50`}
                >
                  <span className="material-symbols-outlined text-xl">
                    {isMarkingResolved ? 'progress_activity' : 'check_circle'}
                  </span>
                  <span>{isMarkingResolved ? 'Updating...' : 'Mark as Resolved'}</span>
                  <span className="material-symbols-outlined text-sm">expand_more</span>
                </button>
                {showStatusDropdown && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-white/10 rounded-lg shadow-xl z-50">
                    <button
                      onClick={() => handleMarkAsResolved('fixed')}
                      className="w-full px-4 py-3 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2 rounded-t-lg"
                    >
                      <span className="material-symbols-outlined text-emerald-500">check_circle</span>
                      Mark as Fixed
                    </button>
                    <button
                      onClick={() => handleMarkAsResolved('false_positive')}
                      className="w-full px-4 py-3 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2 rounded-b-lg border-t border-white/5"
                    >
                      <span className="material-symbols-outlined text-slate-400">block</span>
                      Mark as False Positive
                    </button>
                  </div>
                )}
              </>
            ) : (
              <button
                onClick={handleReopenFinding}
                disabled={isMarkingResolved}
                className={`flex items-center gap-2 ${
                  currentStatus === 'fixed'
                    ? 'bg-emerald-600 hover:bg-emerald-500'
                    : 'bg-slate-600 hover:bg-slate-500'
                } text-white px-5 py-2.5 rounded-lg font-bold transition-all shadow-lg disabled:opacity-50`}
              >
                <span className="material-symbols-outlined text-xl">
                  {isMarkingResolved ? 'progress_activity' : currentStatus === 'fixed' ? 'check_circle' : 'block'}
                </span>
                <span>
                  {isMarkingResolved
                    ? 'Updating...'
                    : currentStatus === 'fixed'
                      ? 'Resolved'
                      : 'False Positive'}
                </span>
              </button>
            )}
          </div>

          {ticketUrl && (
            <a
              href={ticketUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="fixed bottom-10 right-10 bg-green-600 text-white p-4 rounded-xl shadow-2xl flex items-center gap-3 animate-bounce"
            >
              <span className="material-symbols-outlined">launch</span>
              Ticket Created: View Issue
            </a>
          )}
        </div>

        {/* Integration Modal */}
        {showIntegrationModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <div className="bg-gray-900 border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
              <h3 className="text-xl font-bold text-white mb-4">Configure Integration</h3>

              <div className="flex gap-4 mb-6 border-b border-white/10 pb-4">
                <div className="flex-1 py-2 rounded-lg font-medium bg-gray-700 text-white text-center">
                  GitHub
                </div>
              </div>

              <div className="space-y-4">
                {integrationType === 'github' && (
                  <>
                    <input
                      placeholder="Owner (e.g. facebook)"
                      value={config.owner}
                      onChange={(e) => setConfig({ ...config, owner: e.target.value })}
                      className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-gray-500 outline-none"
                    />
                    <input
                      placeholder="Repo (e.g. react)"
                      value={config.repo}
                      onChange={(e) => setConfig({ ...config, repo: e.target.value })}
                      className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-gray-500 outline-none"
                    />
                    <input
                      type="password"
                      placeholder="Personal Access Token"
                      value={config.token}
                      onChange={(e) => setConfig({ ...config, token: e.target.value })}
                      className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-gray-500 outline-none"
                    />
                  </>
                )}
              </div>

              <div className="flex gap-3 mt-8">
                <button
                  onClick={() => setShowIntegrationModal(false)}
                  className="flex-1 bg-white/5 hover:bg-white/10 text-white py-3 rounded-xl font-bold transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveConfig}
                  disabled={isSaving}
                  className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold transition-colors shadow-lg shadow-blue-900/20"
                >
                  {isSaving ? 'Saving...' : 'Save Configuration'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
