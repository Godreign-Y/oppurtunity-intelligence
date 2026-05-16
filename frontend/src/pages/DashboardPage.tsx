/**
 * pages/DashboardPage.tsx
 * Main dashboard page combining analyze form, company list, and signals panel.
 */

import { useState } from 'react';
import { AnalyzeForm } from '../components/dashboard/AnalyzeForm';
import { AnalysisResult } from '../components/dashboard/AnalysisResult';
import { CompanyList } from '../components/dashboard/CompanyList';
import { SignalsPanel } from '../components/dashboard/SignalsPanel';
import { SignalDetail } from '../components/shared/SignalDetail';
import type { AnalyzeResponse, Company, Signal } from '../types';

export function DashboardPage() {
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [companyListKey, setCompanyListKey] = useState(0);

  const handleAnalyzeResult = (result: AnalyzeResponse) => {
    setAnalyzeResult(result);
    // Refresh the company list to show the newly analyzed company
    setCompanyListKey((k) => k + 1);
    setSelectedCompany(null);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center text-white font-display font-bold text-sm">
            OI
          </div>
          <span className="font-display font-bold text-white tracking-tight">
            Opportunity Intel
          </span>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          Career Pages · Engineering Blogs · AI Inference
        </span>
      </header>

      <div className="flex flex-1 min-h-0">
        {/* Sidebar */}
        <aside className="w-64 border-r border-slate-800 p-4 overflow-y-auto shrink-0">
          <CompanyList
            key={companyListKey}
            onSelect={setSelectedCompany}
            selectedName={selectedCompany?.name ?? null}
          />
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
          <AnalyzeForm onResult={handleAnalyzeResult} />

          {analyzeResult && !selectedCompany && (
            <AnalysisResult result={analyzeResult} onSelectSignal={setSelectedSignal} />
          )}

          {selectedCompany && (
            <SignalsPanel companyName={selectedCompany.name} onSelectSignal={setSelectedSignal} />
          )}

          {!analyzeResult && !selectedCompany && (
            <EmptyState />
          )}
        </main>
      </div>

      {selectedSignal && (
        <SignalDetail 
          signal={selectedSignal} 
          onClose={() => setSelectedSignal(null)} 
        />
      )}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center animate-fade-up">
      <div className="w-16 h-16 rounded-2xl bg-surface-50 border border-slate-700 flex items-center justify-center mb-5">
        <span className="text-2xl">🔭</span>
      </div>
      <h3 className="font-display text-xl font-bold text-white mb-2">
        Start Discovering Opportunities
      </h3>
      <p className="text-sm text-slate-400 max-w-sm">
        Enter a product-based company name above to extract intelligence signals
        from their career pages and engineering blogs.
      </p>
      <div className="mt-6 grid grid-cols-2 gap-3 text-left max-w-sm w-full">
        {[
          { label: 'ATS Detection', desc: 'Greenhouse, Lever, Ashby, Workday' },
          { label: 'Blog Parsing', desc: 'RSS feeds + Firecrawl extraction' },
          { label: 'Pain Mapping', desc: 'Infra, DevOps, AI, Security signals' },
          { label: 'AI Inference', desc: 'LLM-powered opportunity scoring' },
        ].map((item) => (
          <div key={item.label} className="bg-surface-50 border border-slate-800 rounded-lg p-3">
            <p className="text-xs font-semibold text-brand-400 font-mono">{item.label}</p>
            <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
