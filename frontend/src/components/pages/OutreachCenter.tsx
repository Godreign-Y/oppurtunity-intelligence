import { useEffect, useMemo, useState } from 'react';
import { ExternalLink, Linkedin, Mail, Search, UserSearch } from 'lucide-react';
import { fetchOutreachRecommendations } from '../../api/client';
import { useCompany } from '../../context/CompanyContext';
import type { OutreachRecommendation } from '../../types';

export function OutreachCenter() {
  const { focusedCompanyName } = useCompany();
  const [items, setItems] = useState<OutreachRecommendation[]>([]);
  const [selected, setSelected] = useState<OutreachRecommendation | null>(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await fetchOutreachRecommendations(focusedCompanyName || undefined);
        setItems(data);
        setSelected(current => current && data.some(item => item.opportunity_id === current.opportunity_id && item.source === current.source) ? current : data[0] ?? null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [focusedCompanyName]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return items;
    return items.filter(item => [
      item.company_name,
      item.opportunity,
      item.source,
      item.practices.map(p => p.practice_name).join(' '),
      item.suggested_personas.join(' '),
    ].join(' ').toLowerCase().includes(needle));
  }, [items, query]);

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight">Outreach &amp; Action Center</h1>
          <p className="text-sm text-slate-400 mt-1">Find decision makers for each scored opportunity and open the right contact path.</p>
        </div>
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            value={query}
            onChange={event => setQuery(event.target.value)}
            placeholder="Search company, practice, persona"
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_420px] gap-6">
        <div className="bg-surface-50 border border-slate-700 rounded-xl overflow-hidden">
          <div className="grid grid-cols-[1.4fr_1fr_120px_120px] gap-3 px-4 py-3 border-b border-slate-800 text-[10px] uppercase tracking-wider font-mono text-slate-500">
            <span>Opportunity</span>
            <span>Practices</span>
            <span>Fit</span>
            <span>Contacts</span>
          </div>
          <div className="divide-y divide-slate-800 max-h-[620px] overflow-y-auto">
            {loading && <div className="p-8 text-center text-slate-500 font-mono text-sm">Loading outreach candidates...</div>}
            {!loading && filtered.length === 0 && <div className="p-8 text-center text-slate-500 font-mono text-sm">No outreach candidates match the current filters.</div>}
            {!loading && filtered.map(item => (
              <button
                key={`${item.source}-${item.opportunity_id}`}
                onClick={() => setSelected(item)}
                className={`w-full grid grid-cols-1 md:grid-cols-[1.4fr_1fr_120px_120px] gap-3 px-4 py-4 text-left transition-colors ${
                  selected?.opportunity_id === item.opportunity_id && selected?.source === item.source
                    ? 'bg-brand-500/10'
                    : 'hover:bg-slate-900/70'
                }`}
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-display font-bold text-white">{item.company_name}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 font-mono">{item.source}</span>
                  </div>
                  <p className="text-sm text-brand-400 mt-1 truncate">{item.opportunity}</p>
                  <p className="text-xs text-slate-500 mt-1 truncate">{item.angle}</p>
                </div>
                <div className="flex flex-wrap gap-1.5 content-start">
                  {item.practices.slice(0, 3).map(practice => (
                    <span key={practice.practice_code} className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-[10px] font-mono">{practice.practice_name}</span>
                  ))}
                </div>
                <div>
                  <span className="inline-flex px-2 py-1 rounded bg-brand-500/20 text-brand-400 text-xs font-mono font-bold">Relanto {item.relanto_relevance_score}</span>
                  <p className="text-[10px] text-slate-500 mt-1">Signal {item.score}</p>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  {item.decision_makers.length} suggested
                </div>
              </button>
            ))}
          </div>
        </div>

        <OpportunityActionPanel item={selected} />
      </div>
    </div>
  );
}

function OpportunityActionPanel({ item }: { item: OutreachRecommendation | null }) {
  if (!item) {
    return <div className="bg-surface-50 border border-slate-700 rounded-xl p-8 text-center text-slate-500 font-mono text-xs">Select an opportunity to see contacts and actions.</div>;
  }

  return (
    <div className="bg-surface-50 border border-slate-700 rounded-xl p-6 space-y-6 h-fit">
      <div>
        <span className="text-[10px] uppercase font-mono tracking-widest text-brand-400">{item.source}</span>
        <h3 className="font-display text-xl font-bold text-white mt-1">{item.company_name}</h3>
        <p className="text-sm text-slate-400 mt-1">{item.opportunity}</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Metric label="Signal Score" value={item.score} />
        <Metric label="Relanto Fit" value={item.relanto_relevance_score} />
      </div>

      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <p className="text-xs font-mono font-bold text-accent uppercase tracking-wider mb-2">Messaging Angle</p>
        <p className="text-sm text-slate-200 leading-relaxed">{item.angle}</p>
      </div>

      <div className="space-y-3">
        <p className="text-xs font-mono text-slate-500 uppercase tracking-wider">Suggested Contacts</p>
        {item.decision_makers.map((person, idx) => (
          <div key={`${person.title}-${idx}`} className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex items-start justify-between gap-4">
            <div className="flex items-start gap-3 min-w-0">
              <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-brand-400"><UserSearch className="w-4 h-4" /></div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-white truncate">{[person.first_name, person.last_name].filter(Boolean).join(' ') || person.title || 'Suggested stakeholder'}</p>
                <p className="text-xs text-slate-400 mt-0.5 truncate">{person.title}</p>
                <p className="text-[10px] text-slate-500 font-mono mt-1">{person.source === 'hunter' ? 'Hunter contact' : 'LinkedIn search'}</p>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
              {person.email && <a href={`mailto:${person.email}`} className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-400 hover:text-white" title={person.email}><Mail className="w-4 h-4" /></a>}
              {person.linkedin_url && <a href={person.linkedin_url} target="_blank" rel="noreferrer" className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-400 hover:text-white" title="Open LinkedIn"><Linkedin className="w-4 h-4" /></a>}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        <p className="text-xs font-mono text-slate-500 uppercase tracking-wider">Practice Fit</p>
        {item.practices.map(practice => (
          <div key={practice.practice_code} className="p-3 bg-slate-950 rounded border border-slate-800">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-brand-400">{practice.practice_name}</span>
              <span className="text-[10px] text-accent font-mono">{practice.relevance_score ?? practice.delivery_strength}/10</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">{practice.description}</p>
          </div>
        ))}
      </div>

      {item.source_url && (
        <a href={item.source_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs font-mono text-brand-400 hover:text-brand-300 underline underline-offset-2">
          Source evidence <ExternalLink className="w-3 h-3" />
        </a>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3">
      <p className="text-[10px] text-slate-500 font-mono uppercase">{label}</p>
      <p className="font-display text-xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}
