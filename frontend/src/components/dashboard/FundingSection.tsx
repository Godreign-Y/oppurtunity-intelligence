import { useState, useEffect } from 'react';
import {
  fetchFundingEvents,
  fetchFundingInsights,
  triggerFundingIngestion
} from '../../api/client';
import type { FundingEvent, FundingInsights } from '../../types';

export function FundingSection() {
  const [events, setEvents] = useState<FundingEvent[]>([]);
  const [insights, setInsights] = useState<FundingInsights | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isIngesting, setIsIngesting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [eventsData, insightsData] = await Promise.all([
        fetchFundingEvents(50),
        fetchFundingInsights()
      ]);
      setEvents(eventsData);
      setInsights(insightsData);
      setError(null);
    } catch (err: any) {
      console.error('Error loading funding signals:', err);
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
      const res = await triggerFundingIngestion();
      setSuccessMsg(res.message || 'Funding pipeline triggered successfully!');
      
      // Poll to reload after a short delay
      setTimeout(async () => {
        await loadData();
      }, 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Funding Ingestion trigger failed.');
    } finally {
      setIsIngesting(false);
    }
  };

  const filteredEvents = events.filter(e => {
    const term = searchTerm.toLowerCase();
    return (
      (e.company_name?.toLowerCase().includes(term) ?? false) ||
      (e.stage?.toLowerCase().includes(term) ?? false) ||
      (e.raw_text?.toLowerCase().includes(term) ?? false)
    );
  });

  if (loading && !insights) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500/30 border-t-brand-500 animate-spin mb-4" />
        <span className="text-sm text-slate-400 font-mono">Querying corporate funding rounds...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Banner / Header Controls */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-surface-50 to-slate-950 border border-slate-800 rounded-2xl p-6 md:p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Corporate Ingestion & Scoring Engine
            </div>
            <h2 className="text-2xl md:text-3xl font-display font-bold text-white tracking-tight">
              💵 Funding round Analytics
            </h2>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Identify newly capitalized product companies raising Seed and Series rounds. Focus your high-ticket IT consulting outreach on companies experiencing rapid scaling pains.
            </p>
          </div>

          <div className="shrink-0">
            <button
              onClick={handleTriggerIngestion}
              disabled={isIngesting}
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-medium text-sm transition-all duration-300 shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2"
            >
              {isIngesting && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
              🚀 Ingest Funding rounds
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
              <span className="text-3xl mb-2 block">💰</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Total Tracked Capital
              </p>
              <h4 className="text-2xl font-bold text-white mt-1">
                ${insights.total_funding}M
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Aggregate capital raised across discovered product companies.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block">📈</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Average Round Value
              </p>
              <h4 className="text-2xl font-bold text-emerald-400 mt-1">
                ${insights.average_funding}M
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Average valuation of newly funded SaaS targets.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block">🔔</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Funding round events
              </p>
              <h4 className="text-2xl font-bold text-white mt-1">
                {insights.events_count}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Volume of capital alerts ingested in intelligence feeds.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block">🏆</span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Lead Priority Rate
              </p>
              <h4 className="text-2xl font-bold text-emerald-400 mt-1">
                High
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Consulting outreach signals prioritized by growth urgency.
              </p>
            </div>
          </div>

          {/* Target prioritization and Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Top Targets */}
            <div className="lg:col-span-2 bg-surface-50 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                <div>
                  <h3 className="text-lg font-bold text-white font-display">
                    High Growth Targets
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Newly funded startups sorted by capital capacity and modernizing capability.
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-semibold">
                  Outreach Ready
                </span>
              </div>

              {insights.top_funded && insights.top_funded.length > 0 ? (
                <div className="divide-y divide-slate-800/40">
                  {insights.top_funded.map((company, idx) => (
                    <div key={company.company_name} className="flex items-center justify-between py-3.5 first:pt-0 last:pb-0">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300 font-mono">
                          {idx + 1}
                        </div>
                        <div>
                          <span className="font-semibold text-slate-100 hover:text-emerald-400 transition-colors cursor-pointer text-sm">
                            {company.company_name}
                          </span>
                          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-0.5">
                            <span>SaaS Platform growth funding round detected</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className="text-sm font-bold text-emerald-400">${company.amount}M</span>
                          <span className="text-xs text-slate-500 ml-1">raised</span>
                        </div>
                        <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 text-[10px] uppercase font-mono font-bold tracking-wider">
                          Priority 1
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10">
                  <span className="text-2xl">🌱</span>
                  <p className="text-sm text-slate-400 mt-2">No funded target accounts registered yet.</p>
                </div>
              )}
            </div>

            {/* Stages Chart */}
            <div className="bg-surface-50 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div>
                <h3 className="text-lg font-bold text-white font-display">
                  Funding stage Distribution
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Aggregate round stage metrics.
                </p>
              </div>

              <div className="space-y-4">
                {insights.stage_distribution?.map((item) => (
                  <div key={item.stage} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 font-semibold uppercase">{item.stage}</span>
                      <span className="text-slate-400 font-mono">{item.count} alerts</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{
                          width: `${
                            (item.count / (insights.stage_distribution.reduce((acc, curr) => acc + curr.count, 0) || 1)) * 100
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
              Corporate Growth Feed
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live corporate investment events extracted from technology news.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Filter by company name or round..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors w-64"
            />
            <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-400 text-xs font-mono font-semibold">
              {filteredEvents.length} Matched
            </span>
          </div>
        </div>

        {filteredEvents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredEvents.map((ev) => (
              <div key={ev.id} className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700/80 transition-colors flex flex-col justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {ev.stage || 'Seed'}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 text-brand-400 text-[10px] font-mono font-bold uppercase">
                      Score: {ev.opportunity_score}
                    </span>
                  </div>
                  <h4 className="font-semibold text-slate-100 line-clamp-1 text-sm md:text-base mb-2">
                    {ev.company_name || 'Target Account'} Raised {ev.amount ? `$${ev.amount}M` : 'Growth Capital'}
                  </h4>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4 line-clamp-3">
                    {ev.raw_text?.replace(/Title:.*\nSummary:/, "") || 'Startup growth details...'}
                  </p>
                </div>

                <div className="flex items-center justify-between border-t border-slate-800/40 pt-4 mt-auto">
                  <div className="text-[10px] text-slate-500 font-mono">
                    {new Date(ev.date).toLocaleDateString()}
                  </div>
                  {ev.source_url && (
                    <a
                      href={ev.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors"
                    >
                      Article Source 🔗
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <span className="text-3xl mb-3 block">💵</span>
            <h4 className="font-semibold text-slate-300 text-base">No fundinground events available.</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
              Please click "Ingest Funding rounds" above to crawl startup news feeds and analyze targeted capitalization signals.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
