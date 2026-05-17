/**
 * hooks/useAnalyze.ts
 * Custom hook for triggering and managing company analysis state.
 */

import { useState, useCallback } from 'react';
import type { PipelineRun } from '../types';
import { startAnalyzeCompany } from '../api/client';

interface UseAnalyzeReturn {
  result: PipelineRun | null;
  loading: boolean;
  error: string | null;
  analyze: (companyName: string, pipelines: string[]) => Promise<void>;
  reset: () => void;
}

export function useAnalyze(): UseAnalyzeReturn {
  const [result, setResult] = useState<PipelineRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (companyName: string, pipelines: string[]) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await startAnalyzeCompany(companyName, pipelines);
      setResult(data);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Analysis failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, analyze, reset };
}
