/**
 * components/shared/SignalDetail.tsx
 * Modal/Detail view for a single intelligence signal.
 */

import { X, ExternalLink, Shield, Zap, Target, BookOpen } from 'lucide-react';
import type { Signal } from '../../types';

interface Props {
  signal: Signal;
  onClose: () => void;
}

export function SignalDetail({ signal, onClose }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface-50 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl animate-zoom-in">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold uppercase tracking-wider ${
              signal.source_type === 'career_page' ? 'bg-purple-500/20 text-purple-400' : 'bg-green-500/20 text-green-400'
            }`}>
              {signal.source_type.replace('_', ' ')}
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Signal ID: {signal.id ? signal.id.slice(0, 8) : 'NEW'}
            </span>
          </div>
          <button 
            onClick={onClose}
            className="p-1 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Title & Stats */}
          <div className="space-y-2">
            <h2 className="text-2xl font-display font-bold text-white leading-tight">
              {signal.role_title || signal.event_type || 'Opportunity Signal'}
            </h2>
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-1.5 text-slate-400">
                <Shield className="w-4 h-4 text-brand-400" />
                <span className="font-semibold text-white">{Math.round(signal.confidence * 100)}%</span> Confidence
              </div>
              {signal.department && (
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Zap className="w-4 h-4 text-purple-400" />
                  Dept: <span className="text-white">{signal.department}</span>
                </div>
              )}
              {signal.seniority && (
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Target className="w-4 h-4 text-accent" />
                  Level: <span className="text-white uppercase">{signal.seniority}</span>
                </div>
              )}
            </div>
          </div>

          {/* Analysis Sections */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* Tech & Pains */}
            <div className="space-y-6">
              <div>
                <p className="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest mb-3">Technologies Detected</p>
                <div className="flex flex-wrap gap-2">
                  {signal.technologies.map(tech => (
                    <span key={tech} className="px-2.5 py-1 bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs rounded-md font-mono">
                      {tech}
                    </span>
                  ))}
                  {signal.technologies.length === 0 && <span className="text-sm text-slate-600 italic">None detected</span>}
                </div>
              </div>

              <div>
                <p className="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest mb-3">Pain Indicators</p>
                <div className="flex flex-wrap gap-2">
                  {signal.pain_indicators.map(pain => (
                    <span key={pain} className="px-2.5 py-1 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-md">
                      {pain.replace(/_/g, ' ')}
                    </span>
                  ))}
                  {signal.pain_indicators.length === 0 && <span className="text-sm text-slate-600 italic">None detected</span>}
                </div>
              </div>
            </div>

            {/* Opportunity & Business */}
            <div className="space-y-6">
              <div>
                <p className="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest mb-3">Opportunity Mapping</p>
                <ul className="space-y-2">
                  {signal.opportunity_mapping.map((opt, i) => (
                    <li key={i} className="text-sm text-accent font-semibold flex items-start gap-2">
                      <Zap className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                      {opt}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest mb-3">Business Implications</p>
                <ul className="space-y-2">
                  {signal.business_implications.map((imp, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-700 mt-1.5 shrink-0" />
                      {imp}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Evidence */}
          <div className="bg-slate-900/50 rounded-xl p-5 border border-slate-800">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="w-4 h-4 text-slate-400" />
              <p className="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest">Extracted Evidence</p>
            </div>
            <ul className="space-y-2">
              {signal.evidence.map((ev, i) => (
                <li key={i} className="text-sm text-slate-400 italic border-l-2 border-slate-700 pl-3 py-0.5">
                  "{ev}"
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            Detected on {new Date(signal.created_at).toLocaleDateString()}
          </div>
          {signal.source_url && (
            <a 
              href={signal.source_url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs font-bold text-brand-400 hover:text-brand-300 transition-colors"
            >
              View Source <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
