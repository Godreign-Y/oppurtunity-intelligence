/**
 * hooks/useSignals.ts
 * Custom hook for fetching and filtering signals for a company.
 */

import { useState, useEffect } from 'react';
import type { Signal } from '../types';
import { fetchSignals } from '../api/client';

interface UseSignalsReturn {
  signals: Signal[];
  careerSignals: Signal[];
  blogSignals: Signal[];
  loading: boolean;
  error: string | null;
}

/**
 * Fetches and categorizes intelligence signals for a given company.
 *
 * @param companyName - The company name to fetch signals for.
 * @returns Categorized signals and loading/error state.
 */
export function useSignals(companyName: string | null): UseSignalsReturn {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!companyName) {
      setSignals([]);
      return;
    }

    setLoading(true);
    setError(null);

    fetchSignals(companyName)
      .then(setSignals)
      .catch(() => setError('Could not load signals for this company.'))
      .finally(() => setLoading(false));
  }, [companyName]);

  return {
    signals,
    careerSignals: signals.filter((s) => s.source_type === 'career_page'),
    blogSignals: signals.filter((s) => s.source_type === 'engineering_blog'),
    loading,
    error,
  };
}
