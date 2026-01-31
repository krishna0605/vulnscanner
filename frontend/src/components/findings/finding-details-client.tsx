'use client';

import React from 'react';
import { FindingDetails } from '@/lib/api';
import { FindingHeader } from './finding-header';
import { FindingStats } from './finding-stats';
import { FindingContent } from './finding-content';
import { FindingRemediation } from './finding-remediation';
import { FindingComments } from './finding-comments';

import { motion } from 'framer-motion';

interface FindingDetailsClientProps {
  finding: FindingDetails;
}

export function FindingDetailsClient({ finding }: FindingDetailsClientProps) {
  return (
    <div className="relative min-h-screen pb-20">
      {/* Animated Background Grid */}
      <div className="fixed inset-0 z-0 pointer-events-none sticky-grid-bg opacity-40"></div>

      <motion.div
        id="finding-details-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        {/* Header */}
        <FindingHeader finding={finding} />

        <main className="grid grid-cols-12 gap-8">
          {/* Left Column: Stats */}
          <aside className="col-span-12 lg:col-span-3">
            <div className="sticky top-8 flex flex-col gap-6">
              <FindingStats finding={finding} />
            </div>
          </aside>

          {/* Center Column: Content */}
          <div className="col-span-12 lg:col-span-6">
            <FindingContent finding={finding} />
            <FindingComments findingId={finding.id} severity={finding.severity} />
          </div>

          {/* Right Column: Remediation & Metadata */}
          <aside className="col-span-12 lg:col-span-3">
            <FindingRemediation finding={finding} />
          </aside>
        </main>
      </motion.div>

      <style jsx global>{`
        .sticky-grid-bg {
          background-size: 50px 50px;
          background-image:
            linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
          mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
        }
      `}</style>
    </div>
  );
}
