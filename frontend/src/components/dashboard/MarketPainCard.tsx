/**
 * components/dashboard/MarketPainCard.tsx
 * Renders a single market pain intelligence signal card.
 */

import type { MarketPainSignal } from '../../types';
import type { DrawerSignal } from '../shared/SignalDetailDrawer';

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-300 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  low: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};

const SEVERITY_DOT: Record<string, string> = {
  critical: 'bg-red-400',
  high: 'bg-orange-400',
  medium: 'bg-yellow-400',
  low: 'bg-slate-500',
};

interface Props {
  signal: MarketPainSignal;
  onClick?: (signal: DrawerSignal) => void;
}

export function MarketPainCard({ signal, onClick }: Props) {
  const severityStyle = SEVERITY_STYLES[signal.severity] ?? SEVERITY_STYLES.low;
  const dotColor = SEVERITY_DOT[signal.severity] ?? SEVERITY_DOT.low;
  const confidencePct = Math.round(signal.confidence * 100);
  const fitPct = Math.round(signal.strategic_fit_score * 100);

  return (
    <div
      onClick={() => onClick?.({ ...signal, source_url: signal.url, company_name: signal.company })}
      className={`w-full text-left bg-surface-50 border rounded-xl p-5 space-y-3 hover:border-brand-500/40 transition-all ${onClick ? 'cursor-pointer' : 'cursor-default'} ${severityStyle}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-1 flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full shrink-0 ${dotColor}`} />
            <p className="font-display font-semibold text-white text-sm truncate">
              {signal.title}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="text-slate-500 font-mono flex items-center gap-1">
              <span className="text-slate-400 font-semibold">
                {signal.source === 'reddit' ? 'Reddit' : signal.source === 'hackernews' ? 'HackerNews' : signal.source === 'f5bot' ? 'F5Bot' : signal.source}
              </span>
              <span className="text-slate-600"></span>
              {signal.source === 'reddit' ? `r/${signal.subreddit}` : signal.subreddit}
            </span>
            <span className="text-slate-600"></span>
            <span className="text-slate-500"> {signal.upvotes}</span>
            {signal.product && (
              <>
                <span className="text-slate-600"></span>
                <span className="text-brand-400 font-mono">{signal.product}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase border ${severityStyle}`}>
            {signal.severity}
          </span>
          <span className="text-xs font-mono text-slate-400">{confidencePct}%</span>
        </div>
      </div>

      {/* Pain category */}
      {signal.pain_category && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Pain:</span>
          <span className="px-2 py-0.5 bg-red-500/10 text-red-400 text-xs rounded font-mono">
            {signal.pain_category.replace(/_/g, ' ')}
          </span>
        </div>
      )}

      {signal.opportunity_category && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Opportunity:</span>
          <span className="px-2 py-0.5 bg-accent/10 text-accent text-xs rounded font-mono">
            {signal.opportunity_category}
          </span>
        </div>
      )}

      {/* Technologies */}
      {signal.technologies.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {signal.technologies.slice(0, 6).map((tech) => (
            <span key={tech} className="px-2 py-0.5 bg-brand-500/10 text-brand-400 text-xs rounded font-mono">
              {tech}
            </span>
          ))}
        </div>
      )}

      {/* Workflow pains */}
      {signal.workflow_pains.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {signal.workflow_pains.slice(0, 4).map((pain) => (
            <span key={pain} className="px-1.5 py-0.5 bg-orange-500/10 text-orange-400 text-[10px] rounded">
              {pain}
            </span>
          ))}
        </div>
      )}

      {/* Strategic fit + practices */}
      {signal.matched_practices.length > 0 && (
        <div className="border-t border-slate-800 pt-2 mt-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider">Strategic Fit</span>
            <span className="text-xs font-mono text-accent">{fitPct}%</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {signal.matched_practices.slice(0, 3).map((p) => (
              <span key={p} className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 text-[10px] rounded">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Source link */}
      {signal.url && (
        <a
          href={signal.url}
          target="_blank"
          rel="noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="block text-[10px] text-slate-500 hover:text-brand-400 font-mono truncate transition-colors"
        >
          {signal.url}
        </a>
      )}
    </div>
  );
}
