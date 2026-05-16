/**
 * components/shared/OpportunitySummary.tsx
 * Compact opportunity mapping summary for the signals panel.
 */

import type { Signal } from '../../types';
import { snakeToTitle } from '../../utils/format';

interface Props {
  signals: Signal[];
}

interface OpportunityEntry {
  label: string;
  count: number;
}

/**
 * Aggregate opportunity mapping mentions across all signals.
 *
 * @param signals - List of signals to aggregate.
 * @returns Array of {label, count} sorted by count descending.
 */
function aggregateOpportunities(signals: Signal[]): OpportunityEntry[] {
  const counter: Record<string, number> = {};
  for (const signal of signals) {
    for (const opp of signal.opportunity_mapping) {
      counter[opp] = (counter[opp] ?? 0) + 1;
    }
  }
  return Object.entries(counter)
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
}

export function OpportunitySummary({ signals }: Props) {
  const opportunities = aggregateOpportunities(signals);

  if (opportunities.length === 0) {
    return null;
  }

  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-5">
      <p className="text-xs text-slate-400 uppercase tracking-widest font-mono mb-4">
        Mapped Opportunities
      </p>
      <div className="space-y-2">
        {opportunities.map(({ label, count }) => {
          const maxCount = opportunities[0].count;
          const widthPct = Math.round((count / maxCount) * 100);
          return (
            <div key={label}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-slate-300">{label}</span>
                <span className="text-xs font-mono text-slate-500">
                  {count} signal{count !== 1 ? 's' : ''}
                </span>
              </div>
              <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-brand-500 rounded-full transition-all duration-500"
                  style={{ width: `${widthPct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
