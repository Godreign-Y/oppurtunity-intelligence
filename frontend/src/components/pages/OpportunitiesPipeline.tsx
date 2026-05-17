import { useEffect, useState } from 'react';
import { Activity, ArrowUpRight, BriefcaseBusiness, Clock, Filter, HeartCrack, Server, Sparkles } from 'lucide-react';
import { fetchRelantoOpportunities, fetchRelantoPractices } from '../../api/client';
import { useCompany } from '../../context/CompanyContext';
import type { RelantoOpportunity, RelantoPractice } from '../../types';
import type { DrawerSignal } from '../shared/SignalDetailDrawer';

const CATEGORIES = ['AI Infrastructure', 'Cloud Migration', 'DevOps Modernization', 'MLOps Scaling', 'Legacy Refactoring', 'Cost Optimization'];

export function OpportunitiesPipeline({ onSelectSignal }: { onSelectSignal?: (s: DrawerSignal) => void }) {
  const { focusedCompanyName } = useCompany();
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedPractice, setSelectedPractice] = useState('All');
  const [selectedOp, setSelectedOp] = useState<RelantoOpportunity | null>(null);
  const [filterPriority, setFilterPriority] = useState('All');
  const [opportunities, setOpportunities] = useState<RelantoOpportunity[]>([]);
  const [practices, setPractices] = useState<RelantoPractice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [ops, prs] = await Promise.all([
          fetchRelantoOpportunities(focusedCompanyName || undefined, selectedPractice === 'All' ? undefined : selectedPractice),
          fetchRelantoPractices().catch(() => []),
        ]);
        setOpportunities(ops);
        setPractices(prs);
        setSelectedOp(current => current && ops.some(op => op.id === current.id && op.source === current.source) ? current : ops[0] ?? null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [focusedCompanyName, selectedPractice]);

  const filteredOps = opportunities.filter(op => {
    if (selectedCategory !== 'All' && op.opportunity_category !== selectedCategory) return false;
    if (filterPriority !== 'All' && op.priority !== filterPriority) return false;
    return true;
  });

  const averageRelantoFit = filteredOps.length
    ? Math.round(filteredOps.reduce((sum, op) => sum + op.relanto_relevance_score, 0) / filteredOps.length)
    : 0;

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div>
        <h1 className="font-display text-3xl font-bold text-white tracking-tight">Opportunities Pipeline</h1>
        <p className="text-sm text-slate-400 mt-1">Prioritize source-backed opportunities by confidence, Relanto relevance, and involved practices.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <OverviewCard title="Total Opportunities" value={filteredOps.length} icon={<Activity className="text-brand-400 w-4 h-4" />} />
        <OverviewCard title="High Priority" value={filteredOps.filter(o => o.priority === 'High').length} icon={<HeartCrack className="text-red-400 w-4 h-4" />} />
        <OverviewCard title="Relanto Fit" value={averageRelantoFit} icon={<Sparkles className="text-accent w-4 h-4" />} />
        <OverviewCard title="Outreach Ready" value={filteredOps.filter(o => o.relanto_relevance_score >= 75).length} icon={<ArrowUpRight className="text-emerald-400 w-4 h-4" />} />
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1 bg-slate-900 border border-slate-800 rounded-lg p-1.5">
        <button onClick={() => setSelectedCategory('All')} className={`px-4 py-1.5 rounded-md text-xs font-semibold font-mono whitespace-nowrap ${selectedCategory === 'All' ? 'bg-brand-500 text-white' : 'text-slate-400 hover:text-white'}`}>All Categories</button>
        {CATEGORIES.map(cat => (
          <button key={cat} onClick={() => setSelectedCategory(cat)} className={`px-4 py-1.5 rounded-md text-xs font-semibold font-mono whitespace-nowrap ${selectedCategory === cat ? 'bg-brand-500 text-white' : 'text-slate-400 hover:text-white'}`}>{cat}</button>
        ))}
      </div>

      <div className="flex flex-col md:flex-row gap-3 md:items-center">
        <div className="flex items-center gap-2">
          <BriefcaseBusiness className="w-4 h-4 text-slate-400" />
          <select className="bg-slate-900 border border-slate-800 rounded px-3 py-2 text-xs text-slate-300 focus:outline-none" value={selectedPractice} onChange={(e) => setSelectedPractice(e.target.value)}>
            <option value="All">All Relanto Practices</option>
            {practices.map(practice => (
              <option key={practice.practice_code} value={practice.practice_code}>{practice.practice_name}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select className="bg-slate-900 border border-slate-800 rounded px-3 py-2 text-xs text-slate-300 focus:outline-none" value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
            <option value="All">All Priority</option>
            <option value="High">High Only</option>
            <option value="Medium">Medium Only</option>
            <option value="Low">Low Only</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-surface-50 border border-slate-700 rounded-xl p-5">
          <h3 className="font-display font-bold text-white text-base mb-4">Opportunities Feed</h3>
          <div className="space-y-3">
            {loading && <div className="text-center py-12 text-slate-500 font-mono text-sm">Loading opportunities...</div>}
            {!loading && filteredOps.map(op => (
              <button key={`${op.source}-${op.id}`} onClick={() => setSelectedOp(op)} className={`w-full text-left p-4 rounded-lg border transition-all ${selectedOp?.id === op.id && selectedOp?.source === op.source ? 'bg-slate-900 border-brand-500' : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'}`}>
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-display font-bold text-white text-base">{op.company_name}</span>
                      <span className="text-xs text-slate-500 font-mono">{op.opportunity_category}</span>
                    </div>
                    <h4 className="text-sm font-semibold text-brand-400 mt-1">{op.title}</h4>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="block text-xs px-2 py-0.5 rounded-full font-mono font-semibold bg-brand-500/20 text-brand-400 border border-brand-900">Fit {op.relanto_relevance_score}</span>
                    <span className="block text-[10px] text-slate-500 font-mono mt-1">Signal {op.score}</span>
                  </div>
                </div>
                <p className="text-xs text-slate-350 mt-2 line-clamp-2">{op.body || op.reason}</p>
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {op.practices.slice(0, 3).map(practice => (
                    <span key={practice.practice_code} className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-[10px] font-mono">{practice.practice_name}</span>
                  ))}
                </div>
                <div className="flex justify-between items-center mt-3 pt-3 border-t border-slate-800 text-[11px] text-slate-500 font-mono">
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {op.source}</span>
                  <span className="text-accent font-semibold">{op.priority}</span>
                </div>
              </button>
            ))}
            {!loading && filteredOps.length === 0 && <div className="text-center py-12 text-slate-500 font-mono text-sm">No opportunities match selection.</div>}
          </div>
        </div>

        <div>
          {selectedOp ? (
            <div className="bg-surface-50 border border-slate-700 rounded-xl p-6 space-y-6">
              <div>
                <span className="text-[10px] uppercase font-mono tracking-widest text-brand-400">{selectedOp.opportunity_category}</span>
                <h3 className="font-display text-xl font-bold text-white mt-1">{selectedOp.company_name}</h3>
                <h4 className="text-sm font-semibold text-slate-400 mt-1">{selectedOp.title}</h4>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Score label="Signal Confidence" value={selectedOp.score} />
                <Score label="Relanto Relevance" value={selectedOp.relanto_relevance_score} />
              </div>
              <div className="space-y-2">
                <p className="text-xs font-mono text-slate-500 uppercase tracking-wider">Relanto Fit</p>
                <p className="text-sm text-slate-300 leading-relaxed">{selectedOp.reason}</p>
              </div>
              <div className="space-y-3">
                <p className="text-xs font-mono text-slate-500 uppercase tracking-wider">Practices Involved</p>
                {selectedOp.practices.map(practice => (
                  <div key={practice.practice_code} className="text-xs text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-white">{practice.practice_name}</span>
                      <span className="font-mono text-accent">{practice.relevance_score ?? practice.delivery_strength}/10</span>
                    </div>
                    <p className="text-slate-500 mt-1 line-clamp-2">{practice.description}</p>
                  </div>
                ))}
              </div>
              {selectedOp.past_deals.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-mono text-slate-500 uppercase tracking-wider">Relevant Past Work</p>
                  {selectedOp.past_deals.slice(0, 2).map((deal, idx) => (
                    <div key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-900 p-2.5 rounded border border-slate-800">
                      <Server className="w-3.5 h-3.5 text-brand-400 shrink-0 mt-0.5" /> {deal.project_name}
                    </div>
                  ))}
                </div>
              )}
              <button onClick={() => onSelectSignal?.({ ...selectedOp, title: selectedOp.title, source: selectedOp.source, source_url: selectedOp.source_url, body: selectedOp.body, technologies: selectedOp.technologies, pain_indicators: selectedOp.pain_indicators, company_name: selectedOp.company_name })} className="w-full px-3 py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-lg text-xs font-mono transition-colors">Open Source Detail</button>
            </div>
          ) : (
            <div className="bg-surface-50 border border-slate-700 rounded-xl p-6 text-center text-slate-500 py-24 font-mono text-xs">Select an opportunity on the left.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function OverviewCard({ title, value, icon }: { title: string; value: number | string; icon: React.ReactNode }) {
  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-4 flex justify-between items-center hover:border-slate-600 transition-all">
      <div>
        <p className="text-xs text-slate-400 font-medium">{title}</p>
        <p className="font-display font-bold text-white text-xl mt-1 leading-none">{value}</p>
      </div>
      <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 shrink-0">{icon}</div>
    </div>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3">
      <p className="text-[10px] text-slate-500 font-mono uppercase">{label}</p>
      <p className="font-display text-xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}
