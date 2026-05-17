import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import type { PipelineRun } from '../../types';
import { startAnalyzeCompany } from '../../api/client';

interface Props {
  onResult: (result: PipelineRun) => void;
  onCompanySearch?: (company: string) => void;
}

const PIPELINES = [
  { id: 'career', label: 'Career Page (ATS)' },
  { id: 'blog', label: 'Engineering Blog' },
  { id: 'market_pain', label: 'Market Pain (Reddit)' },
  { id: 'git_issues', label: 'Git Issues' },
  { id: 'funding', label: 'Funding Intel' },
  { id: 'hiring', label: 'Global Hiring Intel' }
];

export function AnalyzeForm({ onResult, onCompanySearch }: Props) {
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPipelines, setSelectedPipelines] = useState<string[]>(['career', 'blog', 'market_pain']);

  const togglePipeline = (id: string) => {
    setSelectedPipelines(prev => 
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    );
  };

  const handleSubmit = async () => {
    if (!company.trim() || selectedPipelines.length === 0) return;
    setLoading(true);
    setError(null);
    if (onCompanySearch) onCompanySearch(company.trim());
    try {
      const result = await startAnalyzeCompany(company.trim(), selectedPipelines);
      onResult(result);
      setCompany(''); // Reset after starting
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Analysis failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-up">
      <h2 className="font-display text-2xl font-bold mb-1 text-white">
        Analyze a Company
      </h2>
      <p className="text-sm text-slate-400 mb-6">
        Enter a company name and select pipelines to extract intelligence.
      </p>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="Enter a company name"
          className="flex-1 bg-surface-50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors font-mono text-sm"
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !company.trim() || selectedPipelines.length === 0}
          className="flex items-center gap-2 px-5 py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors pulse-glow"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          {loading ? 'Starting...' : 'Start Pipeline'}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4">
        {PIPELINES.map(p => (
          <label key={p.id} className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input 
              type="checkbox" 
              checked={selectedPipelines.includes(p.id)} 
              onChange={() => togglePipeline(p.id)}
              className="rounded border-slate-700 bg-slate-900 text-brand-500 focus:ring-brand-500"
            />
            {p.label}
          </label>
        ))}
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-400 font-mono">{error}</p>
      )}
    </div>
  );
}
