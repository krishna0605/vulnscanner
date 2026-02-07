'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  owaspTop10,
  flashcards,
  codeExamples,
  ctfPlatforms,
  resources,
  securityNews,
  communityLinks,
  OWASPItem,
} from '@/data/academyData';
import MarketingFooter from '@/components/layout/MarketingFooter';

export default function LearnPage() {
  const [activeTab, setActiveTab] = useState<'owasp' | 'flashcards' | 'code' | 'ctf' | 'resources' | 'news' | 'community'>('owasp');
  const [selectedOwasp, setSelectedOwasp] = useState<OWASPItem | null>(null);
  const [currentFlashcard, setCurrentFlashcard] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [selectedCode, setSelectedCode] = useState(0);

  const severityColors = {
    critical: 'bg-red-500/20 text-red-300 border-red-500/30',
    high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    low: 'bg-green-500/20 text-green-300 border-green-500/30',
  };

  const difficultyColors = {
    beginner: 'text-green-400',
    intermediate: 'text-blue-400',
    advanced: 'text-red-400',
    all: 'text-purple-400',
  };

  const typeColors = {
    cheatsheet: 'bg-blue-500/20 text-blue-300',
    tool: 'bg-green-500/20 text-green-300',
    reference: 'bg-purple-500/20 text-purple-300',
  };

  const platformIcons: Record<string, string> = {
    discord: '💬',
    reddit: '🔴',
    twitter: '🐦',
    slack: '💼',
    forum: '📋',
  };

  return (
    <>
      {/* Background */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-stealth-gradient opacity-80" style={{ backgroundImage: 'linear-gradient(135deg, #313131 0%, #414141 50%, #313131 100%)' }}></div>
      <div className="fixed top-[-20%] left-[-10%] w-[600px] h-[600px] bg-white/5 rounded-full blur-[120px] animate-drift"></div>
      <div className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-gray-500/10 rounded-full blur-[120px] animate-drift" style={{ animationDelay: '-5s' }}></div>

      {/* Nav */}
      <nav className="fixed w-full z-50 glass-nav transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <Link href="/" className="flex-shrink-0 flex items-center cursor-pointer group">
              <div className="relative w-10 h-10 mr-3 flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-3xl absolute animate-pulse">shield</span>
                <div className="absolute inset-0 bg-white/10 blur-lg rounded-full"></div>
              </div>
              <span className="font-sans font-bold text-xl tracking-tight text-white">Vuln<span className="text-slate-400">Scanner</span></span>
            </Link>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-1">
                <Link className="text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-full text-sm font-medium transition-all" href="/features">Features</Link>
                <Link className="text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-full text-sm font-medium transition-all" href="/services">Services</Link>
                <Link className="text-white bg-white/10 px-4 py-2 rounded-full text-sm font-medium transition-all shadow-glow" href="/learn">Learn</Link>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              <Link href="/login" className="text-slate-300 hover:text-white px-4 py-2 text-sm font-mono font-medium hover:bg-white/5 rounded-lg transition-all">LOG_IN</Link>
              <Link href="/signup" className="bg-white hover:bg-gray-100 text-black px-6 py-2 rounded-full text-sm font-bold shadow-glow hover:shadow-glow-hover transition-all transform hover:scale-105">GET ACCESS</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="relative pt-32 pb-12 overflow-hidden">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 text-center">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-white text-xs font-mono mb-6 backdrop-blur-md">
            <span className="material-symbols-outlined text-sm mr-2">school</span>
            KNOWLEDGE BASE
          </div>
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-sans font-bold tracking-tight mb-6 leading-tight text-white">
            Security <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500 text-glow">Academy</span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-slate-400 sm:text-xl font-light">
            Master cybersecurity with curated resources, challenges, and community.
          </p>
          
          {/* Stats */}
          <div className="flex justify-center gap-8 mt-10">
            <div className="text-center">
              <div className="text-3xl font-bold text-white">{ctfPlatforms.length}</div>
              <div className="text-xs text-slate-400 font-mono uppercase">CTF Platforms</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">{resources.length}</div>
              <div className="text-xs text-slate-400 font-mono uppercase">Resources</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">{flashcards.length}</div>
              <div className="text-xs text-slate-400 font-mono uppercase">Flashcards</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
        <div className="flex flex-wrap justify-center gap-2">
          {[
            { id: 'owasp', label: 'OWASP Top 10', icon: 'security' },
            { id: 'flashcards', label: 'Flashcards', icon: 'style' },
            { id: 'code', label: 'Code Lab', icon: 'code' },
            { id: 'ctf', label: 'CTF Practice', icon: 'flag' },
            { id: 'resources', label: 'Resources', icon: 'menu_book' },
            { id: 'news', label: 'News', icon: 'newspaper' },
            { id: 'community', label: 'Community', icon: 'groups' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white text-black'
                  : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white border border-white/10'
              }`}
            >
              <span className="material-symbols-outlined text-lg">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">

        {/* OWASP Top 10 */}
        {activeTab === 'owasp' && (
          <div className="grid md:grid-cols-2 gap-4">
            {owaspTop10.map((item) => (
              <button
                key={item.id}
                onClick={() => setSelectedOwasp(item)}
                className="glass-panel rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all text-left group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                      <span className="material-symbols-outlined text-white">{item.icon}</span>
                    </div>
                    <div>
                      <span className="text-xs font-mono text-slate-500">{item.id}</span>
                      <h3 className="text-lg font-bold text-white">{item.title}</h3>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full border ${severityColors[item.severity]}`}>
                    {item.severity}
                  </span>
                </div>
                <p className="text-slate-400 text-sm line-clamp-2">{item.description}</p>
                <div className="mt-4 flex items-center text-xs text-slate-500 group-hover:text-white transition-colors">
                  <span>Learn more</span>
                  <span className="material-symbols-outlined text-sm ml-1 group-hover:translate-x-1 transition-transform">arrow_forward</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* OWASP Modal */}
        {selectedOwasp && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={() => setSelectedOwasp(null)}>
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fadeIn" />
            <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto glass-panel rounded-[24px] border border-white/20 animate-slideUp" onClick={(e) => e.stopPropagation()}>
              <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
                      <span className="material-symbols-outlined text-white text-2xl">{selectedOwasp.icon}</span>
                    </div>
                    <div>
                      <span className="text-xs font-mono text-slate-500">{selectedOwasp.id}</span>
                      <h2 className="text-2xl font-bold text-white">{selectedOwasp.title}</h2>
                    </div>
                  </div>
                  <button onClick={() => setSelectedOwasp(null)} className="text-slate-400 hover:text-white">
                    <span className="material-symbols-outlined">close</span>
                  </button>
                </div>
                <p className="text-slate-300 mb-6">{selectedOwasp.description}</p>
                <div className="bg-white/5 rounded-xl p-4 mb-6">
                  <h4 className="text-xs font-mono text-slate-500 uppercase mb-2">Example Attack</h4>
                  <code className="text-sm text-red-300 font-mono">{selectedOwasp.example}</code>
                </div>
                <h4 className="text-xs font-mono text-slate-500 uppercase mb-3">Prevention</h4>
                <ul className="space-y-2">
                  {selectedOwasp.prevention.map((tip, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                      <span className="material-symbols-outlined text-green-400 text-sm mt-0.5">check_circle</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Flashcards */}
        {activeTab === 'flashcards' && (
          <div className="max-w-xl mx-auto">
            <div 
              className="glass-panel rounded-3xl p-8 border border-white/10 min-h-[300px] flex flex-col items-center justify-center cursor-pointer transition-all hover:border-white/20"
              onClick={() => setIsFlipped(!isFlipped)}
            >
              <span className="text-xs font-mono text-slate-500 uppercase mb-4">
                {isFlipped ? 'Answer' : 'Question'} • {currentFlashcard + 1}/{flashcards.length}
              </span>
              <p className={`text-xl text-center font-medium ${isFlipped ? 'text-green-300' : 'text-white'}`}>
                {isFlipped ? flashcards[currentFlashcard].answer : flashcards[currentFlashcard].question}
              </p>
              <span className="text-xs text-slate-500 mt-6">Tap to flip</span>
            </div>
            <div className="flex justify-center gap-4 mt-6">
              <button onClick={() => { setCurrentFlashcard((c) => (c === 0 ? flashcards.length - 1 : c - 1)); setIsFlipped(false); }} className="w-12 h-12 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-all">
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <button onClick={() => { setCurrentFlashcard((c) => (c === flashcards.length - 1 ? 0 : c + 1)); setIsFlipped(false); }} className="w-12 h-12 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-all">
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        )}

        {/* Code Lab */}
        {activeTab === 'code' && (
          <div>
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
              {codeExamples.map((ex, i) => (
                <button
                  key={ex.id}
                  onClick={() => setSelectedCode(i)}
                  className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-all ${
                    selectedCode === i ? 'bg-white text-black font-bold' : 'bg-white/5 text-slate-300 hover:bg-white/10'
                  }`}
                >
                  {ex.title}
                </button>
              ))}
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="glass-panel rounded-2xl p-6 border border-red-500/20">
                <div className="flex items-center gap-2 mb-4">
                  <span className="material-symbols-outlined text-red-400">close</span>
                  <span className="text-sm font-bold text-red-400">Vulnerable Code</span>
                </div>
                <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap bg-black/30 rounded-xl p-4 overflow-x-auto">
                  {codeExamples[selectedCode].vulnerableCode}
                </pre>
              </div>
              <div className="glass-panel rounded-2xl p-6 border border-green-500/20">
                <div className="flex items-center gap-2 mb-4">
                  <span className="material-symbols-outlined text-green-400">check</span>
                  <span className="text-sm font-bold text-green-400">Secure Code</span>
                </div>
                <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap bg-black/30 rounded-xl p-4 overflow-x-auto">
                  {codeExamples[selectedCode].secureCode}
                </pre>
              </div>
            </div>
            <div className="mt-6 glass-panel rounded-2xl p-6 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-blue-400">lightbulb</span>
                <span className="text-sm font-bold text-white">Explanation</span>
              </div>
              <p className="text-slate-300">{codeExamples[selectedCode].explanation}</p>
            </div>
          </div>
        )}

        {/* CTF Practice */}
        {activeTab === 'ctf' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ctfPlatforms.map((platform) => (
              <a
                key={platform.id}
                href={platform.url}
                target="_blank"
                rel="noopener noreferrer"
                className="glass-panel rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all group"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${platform.color} flex items-center justify-center mb-4`}>
                  <span className="material-symbols-outlined text-white text-xl">{platform.icon}</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs font-bold uppercase ${difficultyColors[platform.difficulty]}`}>
                    {platform.difficulty}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-300 transition-colors">{platform.name}</h3>
                <p className="text-slate-400 text-sm mb-4">{platform.description}</p>
                <div className="flex flex-wrap gap-2">
                  {platform.tags.map((tag) => (
                    <span key={tag} className="text-[10px] px-2 py-1 rounded-full bg-white/5 text-slate-400">{tag}</span>
                  ))}
                </div>
              </a>
            ))}
          </div>
        )}

        {/* Resources */}
        {activeTab === 'resources' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource) => (
              <a
                key={resource.id}
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="glass-panel rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                    <span className="material-symbols-outlined text-white">{resource.icon}</span>
                  </div>
                  <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full ${typeColors[resource.type]}`}>
                    {resource.type}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-300 transition-colors">{resource.title}</h3>
                <p className="text-slate-400 text-sm">{resource.description}</p>
              </a>
            ))}
          </div>
        )}

        {/* News */}
        {activeTab === 'news' && (
          <div className="space-y-4">
            {securityNews.map((news) => (
              <a
                key={news.id}
                href={news.url}
                target="_blank"
                rel="noopener noreferrer"
                className="glass-panel rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                    <span className="material-symbols-outlined text-white">
                      {news.type === 'cve' ? 'bug_report' : news.type === 'breach' ? 'warning' : 'info'}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white group-hover:text-blue-300 transition-colors">{news.title}</h3>
                    <span className="text-xs text-slate-500">{news.source}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full border ${severityColors[news.severity]}`}>
                    {news.severity}
                  </span>
                  <span className="material-symbols-outlined text-slate-500 group-hover:translate-x-1 transition-transform">arrow_forward</span>
                </div>
              </a>
            ))}
          </div>
        )}

        {/* Community */}
        {activeTab === 'community' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {communityLinks.map((link) => (
              <a
                key={link.id}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="glass-panel rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-3xl">{platformIcons[link.platform]}</span>
                  {link.members && (
                    <span className="text-xs text-slate-400 bg-white/5 px-2 py-1 rounded-full">{link.members}</span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-300 transition-colors">{link.name}</h3>
                <p className="text-slate-400 text-sm mb-4">{link.description}</p>
                <span className="text-xs font-mono text-slate-500 uppercase">{link.platform}</span>
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <MarketingFooter />
    </>
  );
}
