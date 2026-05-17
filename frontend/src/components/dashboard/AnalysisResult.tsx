/**
 * components/dashboard/AnalysisResult.tsx
 * Displays the AI opportunity analysis result from the pipeline.
 */

import { TrendingUp, Users, Globe, Brain, CheckCircle, AlertTriangle } from 'lucide-react';
import { SignalCard } from '../shared/SignalCard';
import { MarketPainSection } from './MarketPainSection';
import type { AnalyzeResponse, Signal } from '../../types';

interface Props {
  result: AnalyzeResponse;
  onSelectSignal?: (signal: Signal) => void;
}

function ConfidenceBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = pct >= 75 ? 'text-green-400' : pct >= 50 ? 'text-yellow-400' : 'text-red-400';
  return (
    <span className={`font-mono text-lg font-bold ${color}`}>{pct}%</span>
  );
}

export function AnalysisResult({ result, onSelectSignal }: Props) {
  const ai = result.ai_analysis;

  return (
    <div className="mt-8 space-y-5 animate-fade-up">
      {/* Header row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard icon={<TrendingUp className="w-5 h-5 text-brand-400" />} label="Total Signals" value={result.total_signals} />
        <StatCard icon={<Users className="w-5 h-5 text-purple-400" />} label="Career Signals" value={result.career_signals_count} />
        <StatCard icon={<Globe className="w-5 h-5 text-green-400" />} label="Blog Signals" value={result.blog_signals_count} />
        <StatCard icon={<AlertTriangle className="w-5 h-5 text-red-400" />} label="Market Pain" value={result.market_pain_count ?? 0} />
        <StatCard icon={<Brain className="w-5 h-5 text-accent" />} label="ATS Platform" value={result.ats_platform ?? '—'} />
      </div>

      {/* AI Analysis Card */}
      {ai && (
        <div className="bg-surface-50 border border-slate-700 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-bold text-white">
              AI Opportunity Assessment
            </h3>
            <ConfidenceBadge score={ai.confidence} />
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-brand-500/20 text-brand-400 rounded-full text-sm font-semibold">
              {ai.detected_opportunity}
            </span>
          </div>

          <div>
            <p className="text-xs text-slate-400 uppercase tracking-widest mb-2 font-mono">Reasoning</p>
            <ul className="space-y-1">
              {ai.reasoning.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <CheckCircle className="w-3.5 h-3.5 text-green-400 mt-0.5 shrink-0" />
                  {r}
                </li>
              ))}
            </ul>
          </div>

          {ai.recommended_outreach && (
            <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
              <p className="text-xs text-slate-400 uppercase tracking-widest mb-1 font-mono">
                Recommended Outreach
              </p>
              <p className="text-sm font-semibold text-accent">
                → {ai.recommended_outreach.stakeholder}
              </p>
              <p className="text-sm text-slate-300 mt-1">{ai.recommended_outreach.angle}</p>
            </div>
          )}
        </div>
      )}

      {/* Source URLs */}
      {(result.ats_url || result.blog_url) && (
        <div className="flex flex-wrap gap-3">
          {result.ats_url && (
            <a href={result.ats_url} target="_blank" rel="noreferrer"
              className="text-xs font-mono text-brand-400 hover:underline truncate max-w-xs">
              🏢 {result.ats_url}
            </a>
          )}
          {result.blog_url && (
            <a href={result.blog_url} target="_blank" rel="noreferrer"
              className="text-xs font-mono text-green-400 hover:underline truncate max-w-xs">
              📝 {result.blog_url}
            </a>
          )}
        </div>
      )}

      {/* Top Signals Preview */}
      {result.signals && result.signals.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-slate-300 px-1">Extracted Signals</h4>
          <div className="grid gap-3 sm:grid-cols-2">
            {result.signals.slice(0, 10).map((signal, idx) => (
              <SignalCard key={idx} signal={signal} onClick={onSelectSignal} />
            ))}
          </div>
          {result.signals.length > 10 && (
            <p className="text-xs text-slate-500 text-center italic">
              + {result.signals.length - 10} more signals found. Select company in sidebar to view all.
            </p>
          )}
        </div>
      )}

      {/* Market Pain Intelligence Section */}
      {result.market_pain_signals && result.market_pain_signals.length > 0 && (
        <MarketPainSection signals={result.market_pain_signals} />
      )}
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-4 flex items-center gap-3">
      <div className="p-2 rounded-lg bg-slate-800">{icon}</div>
      <div>
        <p className="text-xs text-slate-400">{label}</p>
        <p className="font-display font-bold text-white text-lg leading-tight">{value}</p>
      </div>
    </div>
  );
}
