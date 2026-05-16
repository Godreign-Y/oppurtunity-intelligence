/**
 * components/shared/TechCloud.tsx
 * Displays a frequency-weighted tag cloud of detected technologies.
 */

import type { Signal } from '../../types';
import clsx from 'clsx';

interface Props {
  signals: Signal[];
}

interface TechEntry {
  name: string;
  count: number;
}

/**
 * Aggregate technology mentions across signals.
 *
 * @param signals - List of signals to aggregate from.
 * @returns Array of {name, count} sorted by frequency descending.
 */
function aggregateTechs(signals: Signal[]): TechEntry[] {
  const counter: Record<string, number> = {};
  for (const signal of signals) {
    for (const tech of signal.technologies) {
      counter[tech] = (counter[tech] ?? 0) + 1;
    }
  }
  return Object.entries(counter)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 20);
}

export function TechCloud({ signals }: Props) {
  const techs = aggregateTechs(signals);

  if (techs.length === 0) {
    return (
      <p className="text-sm text-slate-500 text-center py-6">
        No technologies detected yet.
      </p>
    );
  }

  const maxCount = techs[0].count;

  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-5">
      <p className="text-xs text-slate-400 uppercase tracking-widest font-mono mb-4">
        Detected Technologies
      </p>
      <div className="flex flex-wrap gap-2">
        {techs.map(({ name, count }) => {
          const ratio = count / maxCount;
          return (
            <span
              key={name}
              title={`${count} mention${count !== 1 ? 's' : ''}`}
              className={clsx(
                'px-3 py-1 rounded-full font-mono border transition-colors',
                ratio >= 0.7
                  ? 'bg-brand-500/25 border-brand-500/50 text-brand-300 text-sm font-semibold'
                  : ratio >= 0.4
                  ? 'bg-brand-500/12 border-brand-500/30 text-brand-400 text-xs'
                  : 'bg-slate-800 border-slate-700 text-slate-400 text-xs'
              )}
            >
              {name}
              <span className="ml-1.5 opacity-50 text-[10px]">{count}</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
