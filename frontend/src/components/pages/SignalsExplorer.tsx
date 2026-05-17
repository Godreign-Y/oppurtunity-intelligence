import { useState, useEffect } from 'react';
import { 
  Search, 
  Github, 
  Briefcase, 
  DollarSign,
  Globe,
  MessageSquareWarning
} from 'lucide-react';
import { 
  fetchCompanies,
  fetchGitHubSignals, 
  fetchFundingEvents, 
  fetchHiringSignals,
  fetchMarketPainSignals,
  fetchSignals
} from '../../api/client';
import type { GitHubIssueSignal, FundingEvent, HiringSignal, Signal, MarketPainSignal } from '../../types';
import { CompanyFilterBar } from '../shared/CompanyFilterBar';
import { useCompany } from '../../context/CompanyContext';
import type { DrawerSignal } from '../shared/SignalDetailDrawer';

interface SignalsExplorerProps {
  onSelectSignal?: (signal: DrawerSignal) => void;
}

export function SignalsExplorer({ onSelectSignal }: SignalsExplorerProps) {
  const { focusedCompanyName } = useCompany();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState<'all' | 'company' | 'market' | 'git' | 'hiring' | 'funding'>('all');
  const [companySignals, setCompanySignals] = useState<Signal[]>([]);
  const [marketPainSignals, setMarketPainSignals] = useState<MarketPainSignal[]>([]);
  const [gitSignals, setGitSignals] = useState<GitHubIssueSignal[]>([]);
  const [fundingSignals, setFundingSignals] = useState<FundingEvent[]>([]);
  const [hiringSignals, setHiringSignals] = useState<HiringSignal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAll() {
      try {
        setLoading(true);
        const companies = await fetchCompanies().catch(() => []);
        const focusedCompanies = focusedCompanyName
          ? companies.filter(c => c.name.toLowerCase().includes(focusedCompanyName.toLowerCase()))
          : companies.slice(0, 8);
        const [companyRows, marketRows, git, fund, hire] = await Promise.all([
          Promise.all(focusedCompanies.map(c => fetchSignals(c.name).catch(() => []))).then(rows => rows.flat()),
          Promise.all(focusedCompanies.map(c => fetchMarketPainSignals(c.name).catch(() => []))).then(rows => rows.flat()),
          fetchGitHubSignals(20).catch(() => []),
          fetchFundingEvents(20).catch(() => []),
          fetchHiringSignals(20).catch(() => [])
        ]);
        setCompanySignals(companyRows);
        setMarketPainSignals(marketRows);
        setGitSignals(git);
        setFundingSignals(fund);
        setHiringSignals(hire);
      } catch (e) {
        console.error("Failed to load signals explorer data", e);
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, [focusedCompanyName]);

  // Combined search: text query + company focus filter
  const matchesSearch = (text: string) =>
    !searchTerm || text.toLowerCase().includes(searchTerm.toLowerCase());
  const matchesCompany = (name: string) =>
    !focusedCompanyName || name.toLowerCase().includes(focusedCompanyName.toLowerCase());

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight">
            Signals Explorer
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Raw intelligence feed across Git discussions, Reddit frustrations, job postings, and financial announcements.
          </p>
        </div>
        <CompanyFilterBar label="Filter Signals" />
      </div>

      {/* Search + Filter bar */}
      <div className="bg-surface-50 border border-slate-700 rounded-xl p-4 flex flex-col md:flex-row gap-4 items-center">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
          <input 
            type="text"
            placeholder="Search by keyword, technology, or ecosystem..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 font-mono"
          />
        </div>

        <div className="flex gap-2 w-full md:w-auto overflow-x-auto">
          <FilterButton active={activeFilter === 'all'} label="All Sources" onClick={() => setActiveFilter('all')} />
          <FilterButton active={activeFilter === 'company'} label="Company Signals" icon={<Globe className="w-3.5 h-3.5" />} onClick={() => setActiveFilter('company')} />
          <FilterButton active={activeFilter === 'market'} label="Market Pain" icon={<MessageSquareWarning className="w-3.5 h-3.5" />} onClick={() => setActiveFilter('market')} />
          <FilterButton active={activeFilter === 'git'} label="Git Issues" icon={<Github className="w-3.5 h-3.5" />} onClick={() => setActiveFilter('git')} />
          <FilterButton active={activeFilter === 'hiring'} label="Hiring Intel" icon={<Briefcase className="w-3.5 h-3.5" />} onClick={() => setActiveFilter('hiring')} />
          <FilterButton active={activeFilter === 'funding'} label="Funding Events" icon={<DollarSign className="w-3.5 h-3.5" />} onClick={() => setActiveFilter('funding')} />
        </div>
      </div>

      {/* Signal stream */}
      <div className="bg-surface-50 border border-slate-700 rounded-xl p-6">
        <h2 className="font-display font-bold text-white text-lg mb-4">Intelligence Stream</h2>

        {loading ? (
          <div className="py-20 text-center text-slate-500 font-mono text-sm">Loading signals stream...</div>
        ) : (
          <div className="space-y-3">
            {(activeFilter === 'all' || activeFilter === 'company') && companySignals
              .filter(s => matchesSearch(`${s.role_title || ''} ${s.event_type || ''} ${s.evidence?.join(' ') || ''}`) && matchesCompany(s.company_name || ''))
              .map(sig => (
                <SignalRow
                  key={sig.id}
                  title={sig.role_title || sig.event_type || sig.source_type}
                  source={sig.source_type === 'career_page' ? 'Career Page' : 'Engineering Blog'}
                  meta={`${sig.company_name} / ${sig.opportunity_category || 'Uncategorized'}`}
                  body={sig.evidence?.join(' ') || sig.business_implications?.join(' ') || 'No details captured.'}
                  sourceUrl={sig.source_url}
                  icon={<Globe className="text-sky-400" />}
                  badge={sig.opportunity_category || 'Signal'}
                  badgeColor="bg-sky-950/60 text-sky-400 border-sky-900"
                  onClick={() => onSelectSignal?.({ ...sig, title: sig.role_title || sig.event_type || sig.source_type, body: sig.evidence?.join('\n') })}
                />
              ))}

            {(activeFilter === 'all' || activeFilter === 'market') && marketPainSignals
              .filter(s => matchesSearch(`${s.title} ${s.body}`))
              .map(sig => (
                <SignalRow
                  key={sig.id}
                  title={sig.title}
                  source="Market Pain"
                  meta={`${sig.source} / ${sig.subreddit || 'community'} / ${sig.opportunity_category || 'Uncategorized'}`}
                  body={sig.body}
                  sourceUrl={sig.url}
                  icon={<MessageSquareWarning className="text-red-400" />}
                  badge={sig.severity}
                  badgeColor="bg-red-950/60 text-red-400 border-red-900"
                  onClick={() => onSelectSignal?.({ ...sig, source_url: sig.url, company_name: sig.company, pain_indicators: sig.pain_subcategories })}
                />
              ))}

            {/* Git signals */}
            {(activeFilter === 'all' || activeFilter === 'git') && gitSignals
              .filter(s => matchesSearch(s.title) && matchesCompany(s.org || ''))
              .map(sig => (
                <SignalRow 
                  key={sig.id}
                  title={sig.title}
                  source="GitHub Issues"
                  meta={`@${sig.org || 'Unknown'} / ${sig.repo || 'N/A'}`}
                  body={sig.content}
                  sourceUrl={sig.source_url}
                  icon={<Github className="text-purple-400" />}
                  badge="Dev Pain"
                  badgeColor="bg-purple-950/60 text-purple-400 border-purple-900"
                  onClick={() => onSelectSignal?.({ ...sig, source: 'github_issues', title: sig.title, content: sig.content ?? undefined, source_url: sig.source_url ?? undefined, org: sig.org ?? undefined, repo: sig.repo ?? undefined })}
                />
              ))
            }

            {/* Hiring signals */}
            {(activeFilter === 'all' || activeFilter === 'hiring') && hiringSignals
              .filter(s => matchesSearch(s.job_title) && matchesCompany(s.company_name || ''))
              .map(sig => (
                <SignalRow 
                  key={sig.id}
                  title={sig.job_title}
                  source="Job Board Ingestion"
                  meta={`Tech stack: ${sig.detected_tech_stack?.join(', ') || 'N/A'}`}
                  body={sig.sanitized_description}
                  sourceUrl={sig.source_url}
                  icon={<Briefcase className="text-brand-400" />}
                  badge="Hiring Spike"
                  badgeColor="bg-brand-950/60 text-brand-400 border-brand-900"
                  onClick={() => onSelectSignal?.({ ...sig, title: sig.job_title, source: 'hiring_signals', source_url: sig.source_url, technologies: sig.detected_tech_stack, body: sig.sanitized_description, company_name: sig.company_name })}
                />
              ))
            }

            {/* Funding signals */}
            {(activeFilter === 'all' || activeFilter === 'funding') && fundingSignals
              .filter(s => matchesSearch(s.company_name || '') && matchesCompany(s.company_name || ''))
              .map(sig => (
                <SignalRow 
                  key={sig.id}
                  title={`${sig.company_name || 'Unknown'} raises $${sig.amount ?? 'N/A'}M in ${sig.stage || 'Series B'}`}
                  source="Funding Announcement"
                  meta={`Event date: ${sig.date}`}
                  body={sig.raw_text || `Company secured ${sig.stage} funding.`}
                  sourceUrl={sig.source_url}
                  icon={<DollarSign className="text-emerald-400" />}
                  badge="Funding Event"
                  badgeColor="bg-emerald-950/60 text-emerald-400 border-emerald-900"
                  onClick={() => onSelectSignal?.({ ...sig, title: `${sig.company_name}  ${sig.stage}`, source: 'funding', source_url: sig.source_url, raw_text: sig.raw_text, company_name: sig.company_name })}
                />
              ))
            }

            {/* Empty state */}
            {!loading && companySignals.length === 0 && marketPainSignals.length === 0 && gitSignals.length === 0 && hiringSignals.length === 0 && fundingSignals.length === 0 && (
              <div className="py-16 text-center text-slate-500 font-mono text-sm">
                No signals found. Run a pipeline to ingest data.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function FilterButton({ active, label, icon, onClick }: { active: boolean; label: string; icon?: React.ReactNode; onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg text-xs font-semibold font-mono flex items-center gap-1.5 whitespace-nowrap transition-all ${
        active 
          ? 'bg-brand-500 text-white shadow-sm' 
          : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function SignalRow({ title, source, meta, body, icon, badge, badgeColor, sourceUrl, onClick }: { 
  title: string; source: string; meta: string; body: string; icon: React.ReactNode; 
  badge: string; badgeColor: string; sourceUrl?: string | null; onClick?: () => void 
}) {
  return (
    <div 
      onClick={onClick}
      className={`p-4 bg-slate-900/60 border border-slate-800 rounded-lg hover:border-slate-600 transition-all flex gap-4 items-start ${onClick ? 'cursor-pointer hover:bg-slate-900' : ''}`}
    >
      <div className="p-2.5 bg-slate-850 rounded-lg border border-slate-800 shrink-0">
        {icon}
      </div>
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-display font-semibold text-white text-sm md:text-base line-clamp-1">{title}</span>
            <span className="text-[10px] text-slate-500 font-mono"> {source}</span>
          </div>
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border uppercase shrink-0 ${badgeColor}`}>
            {badge}
          </span>
        </div>
        <p className="text-xs text-slate-400 font-mono">{meta}</p>
        <p className="text-xs text-slate-300 leading-relaxed line-clamp-2 pt-1">{body}</p>
        {sourceUrl && (
          <a 
            href={sourceUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-[10px] font-mono text-brand-400 hover:text-brand-300 underline underline-offset-2 mt-1"
          >
             View Source
          </a>
        )}
      </div>
    </div>
  );
}

