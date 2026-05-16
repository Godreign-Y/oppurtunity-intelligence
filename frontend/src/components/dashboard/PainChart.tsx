/**
 * components/dashboard/PainChart.tsx
 * Bar chart visualizing pain indicator frequencies across signals.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { Signal } from '../../types';
import { snakeToTitle } from '../../utils/format';

interface Props {
  signals: Signal[];
}

interface ChartDatum {
  name: string;
  count: number;
}

const BAR_COLORS = [
  '#0ea5e9',
  '#8b5cf6',
  '#f59e0b',
  '#10b981',
  '#ef4444',
  '#ec4899',
  '#06b6d4',
];

/**
 * Aggregate pain indicators from a list of signals into chart data.
 *
 * @param signals - List of Signal objects to aggregate.
 * @returns Sorted array of {name, count} objects for recharts.
 */
function buildChartData(signals: Signal[]): ChartDatum[] {
  const counter: Record<string, number> = {};
  for (const signal of signals) {
    for (const pain of signal.pain_indicators) {
      counter[pain] = (counter[pain] ?? 0) + 1;
    }
  }
  return Object.entries(counter)
    .map(([name, count]) => ({ name: snakeToTitle(name), count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
}

export function PainChart({ signals }: Props) {
  const data = buildChartData(signals);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
        No pain indicators detected yet.
      </div>
    );
  }

  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-5">
      <p className="text-xs text-slate-400 uppercase tracking-widest font-mono mb-4">
        Pain Indicator Frequency
      </p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <XAxis
            dataKey="name"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            interval={0}
            angle={-25}
            textAnchor="end"
            height={55}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f1f5f9',
              fontSize: 12,
            }}
            cursor={{ fill: 'rgba(14,165,233,0.08)' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((_, index) => (
              <Cell key={index} fill={BAR_COLORS[index % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
