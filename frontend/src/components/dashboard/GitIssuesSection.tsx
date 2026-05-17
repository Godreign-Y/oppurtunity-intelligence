import { useState, useEffect } from 'react';
import {
  fetchGitInsights,
  fetchGitHubSignals,
  fetchNormalizedSignals,
  ingestGitIssues,
  ingestHFModels,
} from '../../api/client';
import type { GitInsights, GitHubIssueSignal, GitNormalizedSignal } from '../../types';

export function GitIssuesSection() {
  const [insights, setInsights] = useState<GitInsights | null>(null);
  const [githubSignals, setGithubSignals] = useState<GitHubIssueSignal[]>([]);
  const [normalizedSignals, setNormalizedSignals] = useState<GitNormalizedSignal[]>([]);
  
  const [customQuery, setCustomQuery] = useState('');
  const [isIngestingGit, setIsIngestingGit] = useState(false);
  const [isIngestingHF, setIsIngestingHF] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [insightsData, gitData, normData] = await Promise.all([
        fetchGitInsights(),
        fetchGitHubSignals(30),
        fetchNormalizedSignals(30),
      ]);
      setInsights(insightsData);
      setGithubSignals(gitData);
      setNormalizedSignals(normData);
      setError(null);
    } catch (err: any) {
      console.error('Error loading developer pain intelligence:', err);
      setError('Could not connect to the backend server. Make sure it is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleIngestGit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsIngestingGit(true);
    setSuccessMsg(null);
    setError(null);
    try {
      const res = await ingestGitIssues(customQuery || undefined);
      setSuccessMsg(res.message);
      setCustomQuery('');
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'GitHub Ingestion failed.');
    } finally {
      setIsIngestingGit(false);
    }
  };

  const handleIngestHF = async () => {
    setIsIngestingHF(true);
    setSuccessMsg(null);
    setError(null);
    try {
      const res = await ingestHFModels();
      setSuccessMsg(res.message);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Hugging Face Ingestion failed.');
    } finally {
      setIsIngestingHF(false);
    }
  };

  const handleRunAllPipeline = async () => {
    setIsIngestingGit(true);
    setSuccessMsg(null);
    setError(null);
    try {
      // Ingest multiple queries sequentially
      const queries = ["deployment failed", "rollback issue", "latency issue", "outage"];
      const res = await ingestGitIssues(undefined, queries);
      setSuccessMsg(res.message);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Pipeline run failed.');
    } finally {
      setIsIngestingGit(false);
    }
  };

  if (loading && !insights) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500/30 border-t-brand-500 animate-spin mb-4" />
        <span className="text-sm text-slate-400 font-mono">Loading developer intelligence pipelines...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Banner and Quick Ingest Controls */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-surface-50 to-slate-950 border border-slate-800 rounded-2xl p-6 md:p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
              Developer Pain & Ecosystem Signal Engine
            </div>
            <h2 className="text-2xl md:text-3xl font-display font-bold text-white tracking-tight">
              Ecosystem & Git Issues Analytics
            </h2>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Detect active enterprise workflow bottlenecks, cloud failures, and AI-infra deployment crashes from GitHub issues and Hugging Face model discussion channels.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 shrink-0">
            <button
              onClick={handleRunAllPipeline}
              disabled={isIngestingGit}
              className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-medium text-sm transition-all duration-300 shadow-lg shadow-brand-500/20 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2"
            >
              {isIngestingGit && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
               Run Core Pipelines
            </button>
            <button
              onClick={handleIngestHF}
              disabled={isIngestingHF}
              className="px-4 py-2.5 rounded-lg bg-surface-50 border border-slate-700 hover:border-slate-500 text-white font-medium text-sm transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2"
            >
              {isIngestingHF && <div className="w-4 h-4 border-2 border-slate-500/30 border-t-slate-400 rounded-full animate-spin" />}
               Ingest Hugging Face
            </button>
          </div>
        </div>

        {/* Custom Ingestion Search Form */}
        <form onSubmit={handleIngestGit} className="mt-6 flex flex-col sm:flex-row gap-3 max-w-2xl border-t border-slate-800/60 pt-6">
          <input
            type="text"
            placeholder="Search custom issues (e.g. 'Kubernetes cluster fail', 'CUDA out of memory')..."
            value={customQuery}
            onChange={(e) => setCustomQuery(e.target.value)}
            disabled={isIngestingGit}
            className="flex-1 px-4 py-2.5 bg-slate-900/60 border border-slate-800 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isIngestingGit || !customQuery}
            className="px-4 py-2.5 bg-slate-100 hover:bg-white text-slate-950 font-semibold text-sm rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
          >
             Ingest Custom Query
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-xs font-mono">
             {error}
          </div>
        )}
        {successMsg && (
          <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-xs font-mono">
             {successMsg}
          </div>
        )}
      </div>

      {insights && (
        <>
          {/* Executive Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
              <span className="text-3xl mb-2 block"></span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Direct Consulting Leads
              </p>
              <h4 className="text-2xl font-bold text-white mt-1">
                {insights.high_severity_organizations?.length || 0}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                High-severity organizations needing workflow & infra modernization.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block"></span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Ecosystem Health
              </p>
              <h4 className="text-2xl font-bold text-white mt-1">
                {insights.ecosystem_distribution?.reduce((acc, curr) => acc + curr.count, 0) || 0}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Total analyzed signals across cloud and AI environments.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block"></span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                Normalized Signals
              </p>
              <h4 className="text-2xl font-bold text-brand-400 mt-1">
                {normalizedSignals.length}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Structured records produced by the normalization pipeline.
              </p>
            </div>

            <div className="bg-surface-50 border border-slate-800 rounded-xl p-5">
              <span className="text-3xl mb-2 block"></span>
              <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider font-mono">
                High Severity Crashes
              </p>
              <h4 className="text-2xl font-bold text-rose-500 mt-1">
                {insights.severity_distribution?.find(s => s.severity === 'high')?.count || 0}
              </h4>
              <p className="text-xs text-slate-400 mt-2">
                Urgent outages and deployment instability issues currently logged.
              </p>
            </div>
          </div>

          {/* Primary Insights Dashboard and Target Accounts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Direct Consulting Sales Targets */}
            <div className="lg:col-span-2 bg-surface-50 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                <div>
                  <h3 className="text-lg font-bold text-white font-display">
                    Direct Consulting Target Accounts
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Enterprises ranked by quantity of high-severity developer workflow failures.
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-mono font-semibold">
                  Consulting Leads
                </span>
              </div>

              {insights.high_severity_organizations?.length > 0 ? (
                <div className="divide-y divide-slate-800/40">
                  {insights.high_severity_organizations.map((org, index) => (
                    <div key={org.org} className="flex items-center justify-between py-3.5 first:pt-0 last:pb-0 group">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300 font-mono">
                          {index + 1}
                        </div>
                        <div>
                          <span className="font-semibold text-slate-100 hover:text-brand-400 transition-colors cursor-pointer text-sm">
                            {org.org}
                          </span>
                          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-0.5">
                            <span>High-severity outages detected in ecosystem</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className="text-sm font-bold text-rose-400">{org.count}</span>
                          <span className="text-xs text-slate-500 ml-1">failures</span>
                        </div>
                        <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-500 border border-rose-500/20 text-[10px] uppercase font-mono font-bold tracking-wider">
                          Urgently Needed
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10">
                  <span className="text-2xl"></span>
                  <p className="text-sm text-slate-400 mt-2">No high-severity target accounts registered yet.</p>
                  <p className="text-xs text-slate-500 mt-1">Run core pipelines above to trigger automated discovery.</p>
                </div>
              )}
            </div>

            {/* Distribution Charts panel */}
            <div className="bg-surface-50 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div>
                <h3 className="text-lg font-bold text-white font-display">
                  Developer Pain Vectors
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Aggregate severity and cloud/AI distributions.
                </p>
              </div>

              {/* Ecosystem Distribution */}
              <div className="space-y-3">
                <h4 className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider">
                  Ecosystem Distribution
                </h4>
                {insights.ecosystem_distribution?.map((item) => (
                  <div key={item.ecosystem} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 font-semibold uppercase">{item.ecosystem}</span>
                      <span className="text-slate-400 font-mono">{item.count} signals</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-brand-500 rounded-full"
                        style={{
                          width: `${
                            (item.count /
                              (insights.ecosystem_distribution.reduce((acc, curr) => acc + curr.count, 0) || 1)) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Severity Distribution */}
              <div className="space-y-3 pt-4 border-t border-slate-800/60">
                <h4 className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider">
                  Severity Distribution
                </h4>
                {insights.severity_distribution?.map((item) => (
                  <div key={item.severity} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 font-semibold uppercase">{item.severity}</span>
                      <span className="text-slate-400 font-mono">{item.count} signals</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          item.severity === 'high'
                            ? 'bg-rose-500'
                            : item.severity === 'medium'
                            ? 'bg-amber-500'
                            : 'bg-emerald-500'
                        }`}
                        style={{
                          width: `${
                            (item.count /
                              (insights.severity_distribution.reduce((acc, curr) => acc + curr.count, 0) || 1)) *
                            100
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

      {/* Normalized Signals List */}
      <div className="bg-surface-50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-6">
          <div>
            <h3 className="text-lg font-bold text-white font-display">
              Normalized Intelligence Feed
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Refined, structured ecosystem insights matching target organizations and severe software problems.
            </p>
          </div>
          <span className="px-2.5 py-1 rounded bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-mono font-semibold">
            {normalizedSignals.length} Active Signals
          </span>
        </div>

        {normalizedSignals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {normalizedSignals.map((sig) => (
              <div key={sig.id} className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700/80 transition-colors flex flex-col justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase ${
                        sig.severity === 'high'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : sig.severity === 'medium'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}
                    >
                      {sig.severity} Severity
                    </span>
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 text-brand-400 text-[10px] font-mono font-bold uppercase">
                      {sig.signal_type}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[10px] font-mono font-bold uppercase">
                      {sig.ecosystem}
                    </span>
                  </div>
                  <h4 className="font-semibold text-slate-100 line-clamp-2 text-sm md:text-base mb-2">
                    {sig.title}
                  </h4>
                  <div className="flex items-center gap-2 text-xs text-slate-500 mb-4 font-mono">
                    <span>Org: <strong className="text-slate-400">{sig.org || 'Unknown'}</strong></span>
                    <span></span>
                    <span>Repo: <strong className="text-slate-400">{sig.repo || 'N/A'}</strong></span>
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-slate-800/40 pt-4 mt-auto">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Confidence:</span>
                    <span className="text-xs font-bold text-slate-300">{(sig.confidence * 100).toFixed(0)}%</span>
                  </div>
                  {sig.source_url && (
                    <a
                      href={sig.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors"
                    >
                      View Source 
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <span className="text-3xl mb-3 block"></span>
            <h4 className="font-semibold text-slate-300 text-base">No normalized signals available yet.</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
              Please click "Run Core Pipelines" above to ingest issues and generate intelligence indicators automatically.
            </p>
          </div>
        )}
      </div>

      {/* Raw Signal Feed logs */}
      <div className="bg-surface-50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
          <div>
            <h3 className="text-lg font-bold text-white font-display">
              Raw GitHub Signal Feed
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live streamed search data containing raw developer bug reports and incident logs.
            </p>
          </div>
          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 text-xs font-mono font-semibold">
            {githubSignals.length} Active Records
          </span>
        </div>

        {githubSignals.length > 0 ? (
          <div className="max-h-96 overflow-y-auto space-y-3.5 pr-2 divide-y divide-slate-800/40">
            {githubSignals.map((sig) => (
              <div key={sig.id} className="pt-3.5 first:pt-0 group">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h5 className="font-semibold text-slate-200 text-sm group-hover:text-brand-400 transition-colors line-clamp-1">
                      {sig.title}
                    </h5>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                      {sig.content}
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {sig.org && (
                        <span className="px-2 py-0.5 rounded bg-slate-900/80 text-[10px] text-slate-400 border border-slate-800/60 font-mono">
                          @{sig.org}
                        </span>
                      )}
                      {sig.repo && (
                        <span className="px-2 py-0.5 rounded bg-slate-900/80 text-[10px] text-slate-400 border border-slate-800/60 font-mono">
                          {sig.repo}
                        </span>
                      )}
                      {sig.labels?.map((lbl) => (
                        <span key={lbl} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-500 font-mono">
                          {lbl}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="shrink-0 text-right text-xs text-slate-500 font-mono">
                    <div>{sig.comments || 0} comments</div>
                    <div className="mt-1">{sig.created_at ? new Date(sig.created_at).toLocaleDateString() : ''}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-10">
            <p className="text-sm text-slate-500">No raw GitHub records available.</p>
          </div>
        )}
      </div>
    </div>
  );
}
