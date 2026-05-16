/**
 * hooks/useAnalyze.ts
 * Custom hook for triggering and managing company analysis state.
 */

import { useState, useCallback } from 'react';
import type { AnalyzeResponse } from '../types';
import { analyzeCompany } from '../api/client';

interface UseAnalyzeReturn {
  result: AnalyzeResponse | null;
  loading: boolean;
  error: string | null;
  analyze: (companyName: string) => Promise<void>;
  reset: () => void;
}

/**
 * Manages state for the company analysis pipeline trigger.
 *
 * @returns State and handlers for analysis lifecycle.
 */
export function useAnalyze(): UseAnalyzeReturn {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (companyName: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeCompany(companyName);
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
