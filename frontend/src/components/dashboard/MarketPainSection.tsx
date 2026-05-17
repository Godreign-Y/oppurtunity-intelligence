/**
 * components/dashboard/MarketPainSection.tsx
 * Renders the market pain intelligence section in the analysis results.
 */

import type { MarketPainSignal } from '../../types';
import { MarketPainCard } from './MarketPainCard';
import type { DrawerSignal } from '../shared/SignalDetailDrawer';

interface Props {
  signals: MarketPainSignal[];
  onSelectSignal?: (signal: DrawerSignal) => void;
}

export function MarketPainSection({ signals, onSelectSignal }: Props) {
  if (!signals || signals.length === 0) {
    return null;
  }

  // Compute summary stats
  const categories: Record<string, number> = {};
  const severities: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  const practices = new Set<string>();

  signals.forEach((s) => {
    if (s.pain_category) {
      categories[s.pain_category] = (categories[s.pain_category] || 0) + 1;
    }
    severities[s.severity] = (severities[s.severity] || 0) + 1;
    s.matched_practices?.forEach((p) => practices.add(p));
  });

  const sortedCategories = Object.entries(categories)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className="space-y-4 animate-fade-up">
      {/* Section header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
          <h3 className="font-display text-lg font-bold text-white">
            Market Pain Intelligence
          </h3>
          <span className="text-xs text-slate-500 font-mono">
            {signals.length} signal{signals.length !== 1 ? 's' : ''} from {
              Array.from(new Set(signals.map(s => s.source === 'reddit' ? 'Reddit' : s.source === 'hackernews' ? 'HackerNews' : s.source === 'f5bot' ? 'F5Bot' : s.source))).join(' & ')
            }
          </span>
        </div>
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Severity breakdown */}
        <div className="bg-surface-50 border border-slate-800 rounded-lg p-3">
          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Severity</p>
          <div className="flex items-center gap-2">
            {severities.critical > 0 && (
              <span className="text-xs text-red-400 font-mono">{severities.critical} critical</span>
            )}
            {severities.high > 0 && (
              <span className="text-xs text-orange-400 font-mono">{severities.high} high</span>
            )}
            {severities.medium > 0 && (
              <span className="text-xs text-yellow-400 font-mono">{severities.medium} med</span>
            )}
          </div>
        </div>

        {/* Top pain category */}
        {sortedCategories.length > 0 && (
          <div className="bg-surface-50 border border-slate-800 rounded-lg p-3">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Top Pain</p>
            <p className="text-xs text-red-400 font-mono">
              {sortedCategories[0][0].replace(/_/g, ' ')}
            </p>
          </div>
        )}

        {/* Avg confidence */}
        <div className="bg-surface-50 border border-slate-800 rounded-lg p-3">
          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Avg Confidence</p>
          <p className="text-xs text-brand-400 font-mono">
            {Math.round(
              (signals.reduce((a, s) => a + s.confidence, 0) / signals.length) * 100
            )}%
          </p>
        </div>

        {/* Practices matched */}
        <div className="bg-surface-50 border border-slate-800 rounded-lg p-3">
          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Capability Fit</p>
          <p className="text-xs text-emerald-400 font-mono">
            {practices.size} practice{practices.size !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Pain category distribution */}
      {sortedCategories.length > 0 && (
        <div className="bg-surface-50 border border-slate-800 rounded-lg p-4">
          <p className="text-xs text-slate-500 mb-3 uppercase tracking-wider">Pain Distribution</p>
          <div className="space-y-2">
            {sortedCategories.map(([cat, count]) => {
              const pct = Math.round((count / signals.length) * 100);
              return (
                <div key={cat} className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 font-mono w-40 truncate">
                    {cat.replace(/_/g, ' ')}
                  </span>
                  <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500 font-mono w-10 text-right">{pct}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Signal cards */}
      <div className="grid gap-3 sm:grid-cols-2">
        {signals.map((signal) => (
          <MarketPainCard key={signal.id} signal={signal} onClick={onSelectSignal} />
        ))}
      </div>
    </div>
  );
}
