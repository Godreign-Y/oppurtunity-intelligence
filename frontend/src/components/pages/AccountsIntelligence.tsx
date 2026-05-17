import { useState, useEffect } from 'react';
import { CompanyList } from '../dashboard/CompanyList';
import { AnalyzeForm } from '../dashboard/AnalyzeForm';
import { PipelineRunsList } from '../dashboard/PipelineRunsList';
import { AnalysisResult } from '../dashboard/AnalysisResult';
import { SignalsPanel } from '../dashboard/SignalsPanel';
import type { Company, PipelineRun, AnalyzeResponse } from '../../types';
import type { DrawerSignal } from '../shared/SignalDetailDrawer';
import { useCompany } from '../../context/CompanyContext';

interface Props {
  selectedCompany?: Company | null;
  onSelectCompany?: (c: Company | null) => void;
  onSelectSignal?: (signal: DrawerSignal) => void;
}

export function AccountsIntelligence({ selectedCompany, onSelectCompany, onSelectSignal }: Props) {
  const { setFocusedCompany } = useCompany();
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null);
  const [searchedCompany, setSearchedCompany] = useState<string | null>(null);
  const [listKey, setListKey] = useState(0);

  // If a company is selected from elsewhere (e.g. Command Center), reset searchedCompany
  useEffect(() => {
    if (selectedCompany) {
      setSearchedCompany(null);
      setAnalyzeResult(null);
    }
  }, [selectedCompany]);

  const handlePipelineStart = () => {
    setAnalyzeResult(null);
    if (onSelectCompany) onSelectCompany(null);
    setListKey(k => k + 1);
  };

  const handleSelectRun = (run: PipelineRun) => {
    if (run.results) {
      setAnalyzeResult(run.results);
      if (onSelectCompany) onSelectCompany(null);
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 h-full items-start">
      {/* Sidebar List */}
      <div className="w-full md:w-64 shrink-0 bg-surface-50 border border-slate-700 rounded-xl p-4 self-stretch">
        <CompanyList 
          key={listKey}
          onSelect={(c) => {
            setFocusedCompany(c);
            if (onSelectCompany) onSelectCompany(c);
            setAnalyzeResult(null);
            setSearchedCompany(null);
          }}
          selectedName={selectedCompany?.name ?? null}
        />
      </div>

      {/* Main Account details */}
      <div className="flex-1 space-y-6 w-full">
        {/* Form to trigger new analysis */}
        <div className="bg-surface-50 border border-slate-700 rounded-xl p-6">
          <AnalyzeForm 
            onResult={handlePipelineStart} 
            onCompanySearch={setSearchedCompany} 
          />

          {searchedCompany && (
            <PipelineRunsList 
              companyName={searchedCompany} 
              onSelectRun={handleSelectRun} 
            />
          )}
        </div>

        {/* Display profile if selected or analyzed */}
        {selectedCompany && !analyzeResult && (
          <div className="space-y-6">
            {/* Account Header */}
            <div className="bg-surface-50 border border-slate-700 rounded-xl p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <div className="flex items-center gap-2.5">
                  <h2 className="font-display text-2xl font-bold text-white">{selectedCompany.name}</h2>
                </div>
                <p className="text-xs text-slate-400 mt-1 font-mono">
                  ATS detected: {selectedCompany.ats_platform || 'N/A'} | Domain: {selectedCompany.domain || 'N/A'}
                </p>
              </div>
            </div>

            {/* Interactive Signals Panel */}
            <SignalsPanel 
              companyName={selectedCompany.name} 
              onSelectSignal={onSelectSignal}
            />
          </div>
        )}

        {/* Display completed analysis response */}
        {analyzeResult && (
          <AnalysisResult result={analyzeResult} onSelectSignal={onSelectSignal} />
        )}

        {!selectedCompany && !analyzeResult && !searchedCompany && (
          <div className="flex flex-col items-center justify-center py-20 text-center bg-surface-50 border border-slate-700 rounded-xl">
            <div className="w-12 h-12 bg-slate-850 rounded-xl flex items-center justify-center text-xl mb-4 border border-slate-800" />
            <h3 className="font-display text-lg font-bold text-white mb-1">
              Select or Analyze a Target Company
            </h3>
            <p className="text-xs text-slate-400 max-w-sm">
              Use the sidebar to pick a target account or execute a pipeline run above to load opportunity insights.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
