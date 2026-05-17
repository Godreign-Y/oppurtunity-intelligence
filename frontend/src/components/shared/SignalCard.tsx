/**
 * components/shared/SignalCard.tsx
 * Renders a single normalized intelligence signal card.
 */

import type { Signal } from '../../types';
import type { DrawerSignal } from './SignalDetailDrawer';

const SOURCE_STYLES: Record<string, string> = {
  career_page: 'bg-purple-500/20 text-purple-300',
  engineering_blog: 'bg-green-500/20 text-green-300',
};

interface Props {
  signal: Signal;
  onClick?: (signal: DrawerSignal) => void;
  compact?: boolean;
}

function getRelativeTime(timestamp?: string | null) {
  if (!timestamp) return 'Just now';
  const diff = Date.now() - new Date(timestamp).getTime();
  if (isNaN(diff)) return 'Just now';
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  return `${days} days ago`;
}

export function SignalCard({ signal, onClick }: Props) {
  const sourceBadge = SOURCE_STYLES[signal.source_type] ?? 'bg-slate-700 text-slate-300';
  const confidencePct = Math.round(signal.confidence * 100);

  return (
    <div
      onClick={() => onClick?.(signal)}
      className={`w-full text-left bg-surface-50 border border-slate-700 rounded-xl p-5 space-y-3 hover:border-brand-500/50 hover:bg-surface-100 transition-all active:scale-[0.98] ${onClick ? 'cursor-pointer' : 'cursor-default'}`}
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-1">
          {signal.role_title && (
            <div className="flex items-center gap-2">
              <p className="font-display font-semibold text-white">{signal.role_title}</p>
              {signal.urgency === 'High' && (
                <span className="px-1.5 py-0.5 bg-red-500 text-white text-[10px] uppercase font-bold rounded">Urgent</span>
              )}
            </div>
          )}
          <div className="flex items-center gap-2 flex-wrap">
            {signal.event_type && (
              <p className="text-xs text-slate-400 font-mono">{signal.event_type.replace(/_/g, ' ')}</p>
            )}
            {signal.location && (
              <p className="text-xs text-slate-500 font-mono"> {signal.location}</p>
            )}
            {signal.timestamp && (
              <p className="text-xs text-brand-400/80 font-mono italic"> {getRelativeTime(signal.timestamp)}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className={`text-xs px-2 py-0.5 rounded-full font-mono ${sourceBadge}`}>
            {signal.source_type === 'career_page' ? 'Career' : 'Blog'}
          </span>
          <span className="text-xs font-mono text-slate-400">{confidencePct}%</span>
        </div>
      </div>

      {/* Technologies */}
      {signal.technologies.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {signal.technologies.slice(0, 8).map((tech) => (
            <span key={tech} className="px-2 py-0.5 bg-brand-500/10 text-brand-400 text-xs rounded font-mono">
              {tech}
            </span>
          ))}
        </div>
      )}

      {/* Pain indicators */}
      {signal.pain_indicators.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {signal.pain_indicators.map((pain) => (
            <span key={pain} className="px-2 py-0.5 bg-red-500/10 text-red-400 text-xs rounded">
              {pain.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      )}

      {signal.opportunity_category && (
        <div className="inline-flex px-2 py-0.5 bg-accent/10 text-accent text-xs rounded font-mono">
          {signal.opportunity_category}
        </div>
      )}

      {/* Opportunity mapping */}
      {signal.opportunity_mapping.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">Opportunity</p>
          <p className="text-sm text-accent font-medium">{signal.opportunity_mapping[0]}</p>
        </div>
      )}

      {/* Source URL */}
      {signal.source_url && (
        <a
          href={signal.source_url}
          target="_blank"
          rel="noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="block text-xs text-slate-500 hover:text-brand-400 font-mono truncate transition-colors"
        >
          {signal.source_url}
        </a>
      )}
    </div>
  );
}
