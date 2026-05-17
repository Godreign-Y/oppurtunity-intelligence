import { useEffect, useState } from 'react';
import {
  ArrowUpRight,
  Building2,
  ChevronRight,
  Compass,
  DollarSign,
  Radio,
  Search,
  Send,
  ShieldAlert,
  Terminal,
  TrendingUp,
  Users,
} from 'lucide-react';
import {
  fetchCompanies,
  fetchFundingEvents,
  fetchFundingInsights,
  fetchGitInsights,
  fetchHiringInsights,
  fetchHiringSignals,
  fetchOutreachRecommendations,
  fetchPipelineLogs,
  fetchRelantoOpportunities,
} from '../../api/client';
import { useCompany } from '../../context/CompanyContext';
import type { Company, FundingEvent, HiringSignal, RelantoOpportunity } from '../../types';

interface Props {
  onNavigate: (tab: string, company?: Company) => void;
}

export function CommandCenter({ onNavigate }: Props) {
  const { focusedCompanyName } = useCompany();
  const [opportunities, setOpportunities] = useState<RelantoOpportunity[]>([]);
  const [fundingEvents, setFundingEvents] = useState<FundingEvent[]>([]);
  const [hiringSignals, setHiringSignals] = useState<HiringSignal[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [stats, setStats] = useState({
    totalAccounts: 0,
    highSeverity: 0,
    newFunding: 0,
    activeHiring: 0,
    outreachReady: 0,
    scoredOpportunities: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;

    async function loadData() {
      try {
        const [compData, fundIns, hireIns, gitIns, recentFund, recentHire, ops, outreach] = await Promise.all([
          fetchCompanies(),
          fetchFundingInsights().catch(() => ({ events_count: 0 })),
          fetchHiringInsights().catch(() => ({ total_jobs: 0 })),
          fetchGitInsights().catch(() => ({ severity_distribution: [] })),
          fetchFundingEvents(5).catch(() => []),
          fetchHiringSignals(5).catch(() => []),
          fetchRelantoOpportunities(focusedCompanyName || undefined).catch(() => []),
          fetchOutreachRecommendations(focusedCompanyName || undefined).catch(() => []),
        ]);

        if (!alive) return;
        const highSeverityCount = gitIns.severity_distribution
          ?.filter((d: any) => d.severity === 'high' || d.severity === 'critical')
          .reduce((sum: number, d: any) => sum + (d.count || 0), 0) || 0;

        setFundingEvents(recentFund);
        setHiringSignals(recentHire);
        setOpportunities(ops.slice(0, 5));
        setStats({
          totalAccounts: compData.length,
          highSeverity: highSeverityCount,
          newFunding: fundIns.events_count || 0,
          activeHiring: hireIns.total_jobs || 0,
          outreachReady: outreach.filter(item => item.relanto_relevance_score >= 75).length,
          scoredOpportunities: ops.length,
        });
      } finally {
        if (alive) setLoading(false);
      }
    }

    loadData();
    return () => {
      alive = false;
    };
  }, [focusedCompanyName]);

  useEffect(() => {
    let alive = true;
    async function loadLogs() {
      const lines = await fetchPipelineLogs({ companyName: focusedCompanyName || undefined, limit: 80 }).catch(() => []);
      if (alive) setLogs(lines);
    }
    loadLogs();
    const interval = window.setInterval(loadLogs, 2500);
    return () => {
      alive = false;
      window.clearInterval(interval);
    };
  }, [focusedCompanyName]);

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight">Intelligence Command Center</h1>
          <p className="text-sm text-slate-400 mt-1">
            Live source-backed opportunities, trigger events, and pipeline execution output.
          </p>
        </div>
        <div className="inline-flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-xs font-mono text-slate-400">
          <Radio className="w-4 h-4 text-emerald-400" />
          {logs.length > 0 ? 'Pipeline logs connected' : 'Waiting for pipeline activity'}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <MetricCard icon={<Users className="w-5 h-5 text-brand-400" />} label="Accounts" value={stats.totalAccounts} />
        <MetricCard icon={<Compass className="w-5 h-5 text-accent" />} label="Opportunities" value={stats.scoredOpportunities} />
        <MetricCard icon={<ShieldAlert className="w-5 h-5 text-red-400" />} label="High Risk Signals" value={stats.highSeverity} />
        <MetricCard icon={<DollarSign className="w-5 h-5 text-emerald-400" />} label="Funding Events" value={stats.newFunding} />
        <MetricCard icon={<TrendingUp className="w-5 h-5 text-indigo-400" />} label="Hiring Signals" value={stats.activeHiring} />
        <MetricCard icon={<Send className="w-5 h-5 text-sky-400" />} label="Outreach Ready" value={stats.outreachReady} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface-50 border border-slate-700 rounded-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-display text-lg font-bold text-white flex items-center gap-2">
                <Compass className="w-5 h-5 text-brand-400" />
                Top Relanto-Matched Opportunities
              </h2>
              <button onClick={() => onNavigate('opportunities')} className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1 font-mono transition-colors">
                All Opportunities <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-4">
              {loading ? (
                <div className="py-12 text-center text-slate-500 font-mono text-sm">Loading opportunities...</div>
              ) : opportunities.length === 0 ? (
                <div className="py-12 text-center text-slate-500 font-mono text-sm">No scored opportunities found. Run a pipeline to populate this feed.</div>
              ) : (
                opportunities.map(op => (
                  <button key={`${op.source}-${op.id}`} className="w-full text-left p-4 bg-slate-900/60 border border-slate-800 rounded-lg hover:border-brand-500/50 transition-colors" onClick={() => onNavigate('opportunities')}>
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-display font-semibold text-white text-base">{op.company_name}</span>
                          <span className="text-xs px-2 py-0.5 rounded bg-brand-500/20 text-brand-400 font-mono">Fit {op.relanto_relevance_score}</span>
                        </div>
                        <p className="text-xs text-slate-400 font-mono mt-1">{op.opportunity_category} / {op.source}</p>
                      </div>
                      <span className="text-xs text-emerald-400 font-mono bg-emerald-950/60 border border-emerald-900 px-2 py-0.5 rounded">
                        Signal {op.score}
                      </span>
                    </div>
                    <p className="mt-3 text-sm text-slate-300 line-clamp-2">{op.title}</p>
                    <div className="mt-3 pt-3 border-t border-slate-800 flex justify-between items-center gap-3">
                      <span className="text-xs text-slate-500 truncate">{op.practices.map(p => p.practice_name).join(', ') || 'No practice mapping'}</span>
                      <span className="text-xs text-accent font-semibold flex items-center gap-0.5 shrink-0">
                        Review <ChevronRight className="w-3 h-3" />
                      </span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          <PipelineTerminal logs={logs} />
        </div>

        <div className="space-y-6">
          <div className="bg-surface-50 border border-slate-700 rounded-xl p-5">
            <h3 className="font-display text-base font-bold text-white mb-3">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-2">
              <QuickActionButton label="Accounts" icon={<Building2 className="w-4 h-4" />} onClick={() => onNavigate('accounts')} />
              <QuickActionButton label="Opportunities" icon={<ArrowUpRight className="w-4 h-4" />} onClick={() => onNavigate('opportunities')} />
              <QuickActionButton label="Signals" icon={<Search className="w-4 h-4" />} onClick={() => onNavigate('signals')} />
              <QuickActionButton label="Outreach" icon={<Send className="w-4 h-4" />} onClick={() => onNavigate('outreach')} />
            </div>
          </div>

          <div className="bg-surface-50 border border-slate-700 rounded-xl p-5 space-y-4">
            <h3 className="font-display text-base font-bold text-white">Recent Triggers</h3>
            <div>
              <p className="text-xs text-slate-500 font-mono uppercase mb-2">Funding</p>
              <div className="space-y-2">
                {fundingEvents.length === 0 && <EmptyLine text="No funding events found." />}
                {fundingEvents.map(e => (
                  <div key={e.id} className="text-xs flex justify-between gap-2 bg-slate-900 p-2 rounded border border-slate-800">
                    <span className="text-slate-300 font-semibold truncate">{e.company_name || 'Unknown company'}</span>
                    <span className="text-slate-500 font-mono">{e.stage || 'Round'}</span>
                    <span className="text-emerald-400 font-bold">{e.amount ? `$${e.amount}M` : 'N/A'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <p className="text-xs text-slate-500 font-mono uppercase mb-2">Hiring</p>
              <div className="space-y-2">
                {hiringSignals.length === 0 && <EmptyLine text="No hiring signals found." />}
                {hiringSignals.map(s => (
                  <div key={s.id} className="text-xs flex justify-between gap-2 bg-slate-900 p-2 rounded border border-slate-800">
                    <span className="text-slate-300 truncate">{s.company_name || s.job_title}</span>
                    <span className="text-brand-400 font-mono text-[10px] truncate">{s.detected_tech_stack?.slice(0, 2).join(', ') || 'No stack'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PipelineTerminal({ logs }: { logs: string[] }) {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <h3 className="font-display text-base font-bold text-white flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          Pipeline Terminal
        </h3>
        <span className="text-[10px] text-slate-500 font-mono">Auto-refresh 2.5s</span>
      </div>
      <div className="h-72 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed bg-black/40">
        {logs.length === 0 ? (
          <p className="text-slate-500">No pipeline log lines yet. Start a company analysis to watch progress here.</p>
        ) : (
          logs.map((line, index) => <p key={`${index}-${line}`} className="text-slate-300 whitespace-pre-wrap">{line}</p>)
        )}
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number | string }) {
  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-4 flex flex-col justify-between h-24 hover:border-slate-600 transition-colors">
      <div className="flex justify-between items-start">
        <span className="text-xs text-slate-400 font-medium">{label}</span>
        <div className="p-1 rounded-md bg-slate-800">{icon}</div>
      </div>
      <p className="font-display font-bold text-white text-2xl leading-none">{value}</p>
    </div>
  );
}

function QuickActionButton({ label, icon, onClick }: { label: string; icon: React.ReactNode; onClick: () => void }) {
  return (
    <button onClick={onClick} className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-left text-xs font-semibold text-slate-300 hover:border-brand-500 hover:text-white transition-all flex flex-col gap-2">
      <span className="text-brand-400">{icon}</span>
      {label}
    </button>
  );
}

function EmptyLine({ text }: { text: string }) {
  return <div className="text-xs text-slate-500 bg-slate-900 p-2 rounded border border-slate-800">{text}</div>;
}
