/**
 * api/client.ts
 * Axios-based API client for the Opportunity Intelligence Platform backend.
 */

import axios from 'axios';
import type { AnalyzeResponse, Company, Signal } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

/** Trigger the full analysis pipeline for a company. */
export async function analyzeCompany(companyName: string): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>('/analyze', {
    company_name: companyName,
  });
  return data;
}

/** List all tracked companies. */
export async function fetchCompanies(): Promise<Company[]> {
  const { data } = await api.get<Company[]>('/companies');
  return data;
}

/** Fetch signals for a specific company. */
export async function fetchSignals(companyName: string): Promise<Signal[]> {
  const { data } = await api.get<Signal[]>(`/companies/${encodeURIComponent(companyName)}/signals`);
  return data;
}
