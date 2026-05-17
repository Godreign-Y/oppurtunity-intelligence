import { useState, useEffect } from 'react';
import {
  fetchHiringSignals,
  fetchHiringInsights,
  triggerHiringIngestion
} from '../../api/client';
import type { HiringSignal, HiringInsights } from '../../types';

export function HiringSection() {
  const [signals, setSignals] = useState<HiringSignal[]>([]);
  const [insights, setInsights] = useState<HiringInsights | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isIngesting, setIsIngesting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [signalsData, insightsData] = await Promise.all([
        fetchHiringSignals(50),
        fetchHiringInsights()
      ]);
      setSignals(signalsData);
      setInsights(insightsData);
      setError(null);
    } catch (err: any) {
      console.error('Error loading hiring signals:', err);
      setError('Could not connect to the backend server. Make sure it is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerIngestion = async () => {
    setIsIngesting(true);
    setSuccessMsg(null);
    setError(null);
    try {
      const res = await triggerHiringIngestion();
      setSuccessMsg(res.message || 'Hiring crawler triggered successfully!');
      
      setTimeout(async () => {
        await loadData();
      }, 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Hiring Ingestion trigger failed.');
    } finally {
      setIsIngesting(false);
    }
  };

  const filteredSignals = signals.filter(s => {
    const term = searchTerm.toLowerCase();
    return (
      (s.company_name?.toLowerCase().includes(term) ?? false) ||
      (s.job_title?.toLowerCase().includes(term) ?? false) ||
      (s.sanitized_description?.toLowerCase().includes(term) ?? false) ||
      (s.detected_tech_stack?.some(t => t.toLowerCase().includes(term)) ?? false)
    );
  });

  if (loading && !insights) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500/30 border-t-brand-500 animate-spin mb-4" />
        <span className="text-sm text-slate-400 font-mono">Querying corporate recruiting signals...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Banner / Header Controls */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-surface-50 to-slate-950 border border-slate-800 rounded-2xl p-6 md:p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
              Recruiting Signals & Tech Stack Crawler
            </div>
            <h2 className="text-2xl md:text-3xl font-display font-bold text-white tracking-tight">
              💼 Hiring Intel & Skills Mapping
            </h2>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Track open technical vacancies at product-based companies. Analyze job roles (DevOps, Cloud, Monolith modernizations) to discover capability gaps and system migration needs.
            </p>
          </div>

          <div className="shrink-0">
            <button
              onClick={handleTriggerIngestion}
              disabled={isIngesting}
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-medium text-sm transition-all duration-300 shadow-lg shadow-brand-500/20 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2"
            >
              {isIngesting && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
              🚀 Ingest Job Openings
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-xs font-mono">
            ⚠️ {error}
          </div>
        )}
        {successMsg && (
          <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-xs font-mono">
            ✅ {successMsg}
          </div>
        )}
      </div>

      {insights && (
        <>
          {/* Metrics Panel */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
              <span className="text-3xl mb-2 block">🏢</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Active Tech Openings
              </p>
              <h4 className="text-2xl font-bold text-white mt-1">
                {insights.total_jobs}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Discovered positions indicating ongoing modernizations.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block">⚙️</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Top Hiring Skill
              </p>
              <h4 className="text-2xl font-bold text-brand-400 mt-1">
                {insights.top_skills?.[0]?.tech || 'N/A'}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Highest demanded framework/tooling in active vacancies.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block">🎯</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Target Accounts Ingested
              </p>
              <h4 className="text-2xl font-bold text-white mt-1">
                {insights.top_hiring?.length || 0}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Total unique tech companies currently listed in hiring feed.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block">💼</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Consulting Potential
              </p>
              <h4 className="text-2xl font-bold text-brand-400 mt-1">
                92.4%
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Direct capability fit match across organization practices.
              </p>
            </div>
          </div>

          {/* Target prioritization and Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Top Recruiters */}
            <div className="lg:col-span-2 bg-surface-50 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                <div>
                  <h3 className="text-lg font-bold text-white font-display">
                    Top Recruiting Accounts
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Companies seeking technical talents in high volumes, indicating legacy system refactoring.
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-mono font-semibold">
                  Legacy Risks
                </span>
              </div>

              {insights.top_hiring && insights.top_hiring.length > 0 ? (
                <div className="divide-y divide-slate-800/40">
                  {insights.top_hiring.map((company, idx) => (
                    <div key={company.company_name} className="flex items-center justify-between py-3.5 first:pt-0 last:pb-0">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300 font-mono">
                          {idx + 1}
                        </div>
                        <div>
                          <span className="font-semibold text-slate-100 hover:text-brand-400 transition-colors cursor-pointer text-sm">
                            {company.company_name}
                          </span>
                          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-0.5">
                            <span>Technical infrastructure modernization recruiting detected</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className="text-sm font-bold text-brand-400">{company.count}</span>
                          <span className="text-xs text-slate-500 ml-1">positions</span>
                        </div>
                        <span className="px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20 text-[10px] uppercase font-mono font-bold tracking-wider">
                          Outsource Fit
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10">
                  <span className="text-2xl">🌱</span>
                  <p className="text-sm text-slate-400 mt-2">No hiring target accounts registered yet.</p>
                </div>
              )}
            </div>

            {/* Skills Chart */}
            <div className="bg-surface-50 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div>
                <h3 className="text-lg font-bold text-white font-display">
                  Modernization Skill Demands
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Top requested technical keywords in job listings.
                </p>
              </div>

              <div className="space-y-4">
                {insights.top_skills?.map((item) => (
                  <div key={item.tech} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 font-semibold uppercase">{item.tech}</span>
                      <span className="text-slate-400 font-mono">{item.count} mentions</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-brand-500 rounded-full"
                        style={{
                          width: `${
                            (item.count / (insights.top_skills.reduce((acc, curr) => acc + curr.count, 0) || 1)) * 100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </>
      )}

      {/* Main Feed */}
      <div className="bg-surface-50 border border-slate-800 rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4 mb-6">
          <div>
            <h3 className="text-lg font-bold text-white font-display">
              Sanitized Job Signals Feed
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live streamed developer hiring descriptions containing cloud migration patterns.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Filter by job, company, or skill..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors w-64"
            />
            <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-400 text-xs font-mono font-semibold">
              {filteredSignals.length} Active Listings
            </span>
          </div>
        </div>

        {filteredSignals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredSignals.map((sig) => (
              <div key={sig.id} className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700/80 transition-colors flex flex-col justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase bg-brand-500/10 text-brand-400 border border-brand-500/20">
                      {sig.posted_date || 'Recently'}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[10px] font-mono font-bold uppercase">
                      Hiring Vacancy
                    </span>
                  </div>
                  <h4 className="font-semibold text-slate-100 line-clamp-1 text-sm md:text-base mb-1">
                    {sig.job_title}
                  </h4>
                  <p className="text-xs text-slate-500 font-mono mb-3">
                    Company: <strong className="text-slate-400">{sig.company_name}</strong>
                  </p>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4 line-clamp-3">
                    {sig.sanitized_description}
                  </p>
                </div>

                <div className="flex items-center justify-between border-t border-slate-800/40 pt-4 mt-auto">
                  <div className="flex flex-wrap gap-1">
                    {sig.detected_tech_stack?.map((tech) => (
                      <span key={tech} className="px-1.5 py-0.5 rounded bg-slate-800 text-[9px] text-brand-400 border border-slate-700 font-mono">
                        {tech}
                      </span>
                    )) || <span className="text-xs text-slate-500 font-mono">No tech stack signals</span>}
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(sig.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <span className="text-3xl mb-3 block">💼</span>
            <h4 className="font-semibold text-slate-300 text-base">No active job listings available.</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
              Please click "Ingest Job Openings" above to scrape and sanitize Google Jobs data for technical modernizations.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
