/**
 * components/dashboard/AnalyzeForm.tsx
 * Form for triggering company intelligence analysis.
 */

import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import type { AnalyzeResponse } from '../../types';
import { analyzeCompany } from '../../api/client';

interface Props {
  onResult: (result: AnalyzeResponse) => void;
}

export function AnalyzeForm({ onResult }: Props) {
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!company.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCompany(company.trim());
      onResult(result);
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
        Enter a product-based company name to extract intelligence from career pages &amp; engineering blogs.
      </p>

      <div className="flex gap-3">
        <input
          type="text"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="e.g. Vercel, Stripe, Linear"
          className="flex-1 bg-surface-50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors font-mono text-sm"
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !company.trim()}
          className="flex items-center gap-2 px-5 py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors pulse-glow"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-400 font-mono">{error}</p>
      )}
    </div>
  );
}
