/**
 * src/components/shared/SignalDetailDrawer.tsx
 *
 * Slide-in drawer panel showing full details of any clicked signal.
 * Displays source URL as a clickable link, opportunity category badge,
 * technologies, pain indicators, and full body text.
 *
 * Usage:
 *   <SignalDetailDrawer signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
 */

import { useEffect } from 'react';
import {
  X,
  ExternalLink,
  Tag,
  Cpu,
  AlertTriangle,
  Calendar,
  Building2,
  Globe,
} from 'lucide-react';

/** Minimal signal shape accepted by this drawer  works with any source type */
export interface DrawerSignal {
  id?: string | number;
  title?: string;
  /** Source URL to open when "View Source" is clicked */
  source_url?: string | null;
  url?: string | null;
  /** Opportunity category (one of the 6 canonical values) */
  opportunity_category?: string | null;
  /** Body / description text */
  content?: string | null;
  body?: string | null;
  sanitized_description?: string | null;
  raw_text?: string | null;
  /** Metadata arrays */
  technologies?: string[];
  detected_tech_stack?: string[];
  pain_indicators?: string[];
  pain_category?: string | null;
  pain_subcategories?: string[];
  /** Source info */
  source?: string;
  subreddit?: string;
  org?: string;
  repo?: string;
  /** Time */
  created_at?: string | null;
  timestamp?: string | null;
  date?: string | null;
  /** Company */
  company_name?: string | null;
  /** Confidence / scores */
  confidence?: number;
  severity?: string | null;
}

interface SignalDetailDrawerProps {
  signal: DrawerSignal | null;
  onClose: () => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  'AI Infrastructure': 'bg-purple-950/60 border-purple-700 text-purple-300',
  'Cloud Migration': 'bg-sky-950/60 border-sky-700 text-sky-300',
  'DevOps Modernization': 'bg-blue-950/60 border-blue-700 text-blue-300',
  'MLOps Scaling': 'bg-fuchsia-950/60 border-fuchsia-700 text-fuchsia-300',
  'Legacy Refactoring': 'bg-amber-950/60 border-amber-700 text-amber-300',
  'Cost Optimization': 'bg-emerald-950/60 border-emerald-700 text-emerald-300',
};

export function SignalDetailDrawer({ signal, onClose }: SignalDetailDrawerProps) {
  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  if (!signal) return null;

  const sourceUrl = signal.source_url || signal.url;
  const bodyText = signal.content || signal.body || signal.sanitized_description || signal.raw_text;
  const techs = signal.technologies || signal.detected_tech_stack || [];
  const pains = signal.pain_indicators || signal.pain_subcategories || [];
  const timestamp = signal.created_at || signal.timestamp || signal.date;
  const categoryStyle = CATEGORY_COLORS[signal.opportunity_category ?? ''] ?? 'bg-slate-800 border-slate-700 text-slate-300';
  const confidencePercent = signal.confidence != null ? Math.round(signal.confidence * 100) : null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Drawer */}
      <aside className="fixed right-0 top-0 h-full w-full max-w-lg bg-slate-900 border-l border-slate-700 z-50 flex flex-col shadow-2xl animate-slide-in-right">
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-slate-800 gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-1">
              {signal.source ? `Source: ${signal.source}` : 'Signal Detail'}
              {signal.subreddit ? `  r/${signal.subreddit}` : ''}
              {signal.org ? `  ${signal.org}/${signal.repo ?? ''}` : ''}
            </p>
            <h2 className="font-display font-bold text-white text-lg leading-snug line-clamp-3">
              {signal.title ?? 'Untitled Signal'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            aria-label="Close panel"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Badges row */}
        <div className="flex flex-wrap gap-2 px-5 py-3 border-b border-slate-800">
          {signal.opportunity_category && (
            <span className={`px-2.5 py-1 rounded-md border text-[10px] font-mono font-bold uppercase tracking-wider ${categoryStyle}`}>
              {signal.opportunity_category}
            </span>
          )}
          {signal.severity && (
            <span className={`px-2.5 py-1 rounded-md border text-[10px] font-mono font-bold uppercase ${
              signal.severity === 'critical' ? 'bg-red-950/60 border-red-700 text-red-300' :
              signal.severity === 'high' ? 'bg-orange-950/60 border-orange-700 text-orange-300' :
              signal.severity === 'medium' ? 'bg-yellow-950/60 border-yellow-700 text-yellow-300' :
              'bg-slate-800 border-slate-700 text-slate-400'
            }`}>
              {signal.severity} severity
            </span>
          )}
          {confidencePercent != null && (
            <span className="px-2.5 py-1 rounded-md border border-slate-700 bg-slate-800 text-[10px] font-mono text-slate-300">
              {confidencePercent}% confidence
            </span>
          )}
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Source URL */}
          {sourceUrl && (
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center gap-3">
              <Globe className="w-4 h-4 text-brand-400 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-[10px] text-slate-500 font-mono mb-0.5">Source URL</p>
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-brand-400 hover:text-brand-300 text-xs font-mono underline underline-offset-2 truncate block"
                >
                  {sourceUrl}
                </a>
              </div>
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="shrink-0 p-1.5 rounded bg-brand-500/20 hover:bg-brand-500/30 text-brand-400 transition-colors"
                aria-label="Open source URL"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          )}

          {/* Metadata grid */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            {signal.company_name && (
              <MetaCell icon={<Building2 className="w-3 h-3" />} label="Company" value={signal.company_name} />
            )}
            {signal.pain_category && (
              <MetaCell icon={<AlertTriangle className="w-3 h-3" />} label="Pain Category" value={signal.pain_category.replace(/_/g, ' ')} />
            )}
            {timestamp && (
              <MetaCell icon={<Calendar className="w-3 h-3" />} label="Timestamp" value={new Date(timestamp).toLocaleDateString()} />
            )}
          </div>

          {/* Body text */}
          {bodyText && (
            <div>
              <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2">Content</h3>
              <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                {bodyText.length > 1200 ? bodyText.slice(0, 1200) + '' : bodyText}
              </p>
            </div>
          )}

          {/* Technologies */}
          {techs.length > 0 && (
            <div>
              <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Cpu className="w-3 h-3" /> Technologies
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {techs.map((t) => (
                  <span key={t} className="px-2 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono text-slate-300">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Pain indicators */}
          {pains.length > 0 && (
            <div>
              <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Tag className="w-3 h-3" /> Pain Indicators
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {pains.map((p) => (
                  <span key={p} className="px-2 py-0.5 bg-red-950/40 border border-red-900/50 rounded text-[10px] font-mono text-red-300">
                    {p.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

function MetaCell({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="p-2.5 bg-slate-950 border border-slate-800 rounded-lg">
      <p className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1 mb-0.5">
        {icon} {label}
      </p>
      <p className="text-slate-200 font-mono text-xs truncate">{value}</p>
    </div>
  );
}
