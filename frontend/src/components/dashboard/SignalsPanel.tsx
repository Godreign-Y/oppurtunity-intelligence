/**
 * components/dashboard/SignalsPanel.tsx
 * Displays signals, charts, and insights for the currently selected company.
 */

import { useEffect, useState } from 'react';
import type { Signal } from '../../types';
import { fetchSignals, fetchMarketPainSignals } from '../../api/client';
import { SignalCard } from '../shared/SignalCard';
import { PainChart } from './PainChart';
import { TechCloud } from '../shared/TechCloud';
import { OpportunitySummary } from '../shared/OpportunitySummary';
import { MarketPainSection } from './MarketPainSection';
import { Loader2 } from 'lucide-react';
import type { DrawerSignal } from '../shared/SignalDetailDrawer';

interface Props {
  companyName: string;
  onSelectSignal?: (signal: DrawerSignal) => void;
}

export function SignalsPanel({ companyName, onSelectSignal }: Props) {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [marketPainSignals, setMarketPainSignals] = useState<import('../../types').MarketPainSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetchSignals(companyName).catch(() => []),
      fetchMarketPainSignals(companyName).catch(() => [])
    ])
      .then(([sigData, mpData]) => {
        setSignals(sigData);
        setMarketPainSignals(mpData);
      })
      .catch(() => setError('No signals found for this company.'))
      .finally(() => setLoading(false));
  }, [companyName]);

  const careerSignals = signals.filter((s) => s.source_type === 'career_page');
  const blogSignals = signals.filter((s) => s.source_type === 'engineering_blog');

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-500">
        <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading signals
      </div>
    );
  }

  if (error || (signals.length === 0 && marketPainSignals.length === 0)) {
    return <p className="text-sm text-slate-500 text-center py-12">{error || 'No signals found for this company yet.'}</p>;
  }

  return (
    <div className="space-y-6 animate-fade-up">
      {/* Header */}
      <div>
        <h3 className="font-display text-xl font-bold text-white">
          {companyName}
          <span className="text-slate-400 text-sm font-sans font-normal ml-3">
            {signals.length} total signals
          </span>
        </h3>
        <div className="flex gap-4 mt-1">
          <span className="text-xs text-purple-400 font-mono">{careerSignals.length} career</span>
          <span className="text-xs text-green-400 font-mono">{blogSignals.length} blog</span>
          {marketPainSignals.length > 0 && (
            <span className="text-xs text-red-400 font-mono">{marketPainSignals.length} market pain</span>
          )}
        </div>
      </div>

      {/* Visual insights row */}
      {signals.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          <PainChart signals={signals} />
          <OpportunitySummary signals={signals} />
        </div>
      )}

      {/* Tech cloud */}
      {signals.length > 0 && <TechCloud signals={signals} />}

      {/* Career signals */}
      {careerSignals.length > 0 && (
        <Section title="Career Page Signals" count={careerSignals.length}>
          {careerSignals.map((s) => <SignalCard key={s.id} signal={s} onClick={onSelectSignal} />)}
        </Section>
      )}

      {/* Blog signals */}
      {blogSignals.length > 0 && (
        <Section title="Engineering Blog Signals" count={blogSignals.length}>
          {blogSignals.map((s) => <SignalCard key={s.id} signal={s} onClick={onSelectSignal} />)}
        </Section>
      )}

      {/* Market Pain signals */}
      {marketPainSignals.length > 0 && (
        <div className="mt-8">
          <MarketPainSection signals={marketPainSignals} onSelectSignal={onSelectSignal} />
        </div>
      )}
    </div>
  );
}

function Section({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-3">
        <p className="text-sm font-semibold text-slate-300">{title}</p>
        <span className="px-2 py-0.5 bg-surface-100 rounded-full text-xs font-mono text-slate-400">
          {count}
        </span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">{children}</div>
    </div>
  );
}
