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

/** Fetch market pain signals for a specific company. */
export async function fetchMarketPainSignals(companyName: string): Promise<import('../types').MarketPainSignal[]> {
  const { data } = await api.get<import('../types').MarketPainSignal[]>(`/companies/${encodeURIComponent(companyName)}/market_pain`);
  return data;
}

/** Ingest GitHub developer issues and run normalization. */
export async function ingestGitIssues(query?: string, queries?: string[]): Promise<{ status: string; message: string; total_ingested: number }> {
  const { data } = await api.post('/git-issues/ingest', { query, queries });
  return data;
}

/** Ingest Hugging Face trending models. */
export async function ingestHFModels(): Promise<{ status: string; message: string; total_ingested: number }> {
  const { data } = await api.post('/git-issues/huggingface/ingest');
  return data;
}

/** Fetch aggregated developer pain insights and consulting leads. */
export async function fetchGitInsights(): Promise<import('../types').GitInsights> {
  const { data } = await api.get<import('../types').GitInsights>('/git-issues/insights');
  return data;
}

/** Fetch recent raw GitHub developer issues signals. */
export async function fetchGitHubSignals(limit = 50): Promise<import('../types').GitHubIssueSignal[]> {
  const { data } = await api.get<import('../types').GitHubIssueSignal[]>('/git-issues/signals', { params: { limit } });
  return data;
}

/** Fetch normalized developer signals. */
export async function fetchNormalizedSignals(limit = 50): Promise<import('../types').GitNormalizedSignal[]> {
  const { data } = await api.get<import('../types').GitNormalizedSignal[]>('/git-issues/normalized', { params: { limit } });
  return data;
}

/** Trigger startup funding ingestion. */
export async function triggerFundingIngestion(): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>('/funding/ingest');
  return data;
}

/** Fetch recent corporate funding events. */
export async function fetchFundingEvents(limit = 50): Promise<import('../types').FundingEvent[]> {
  const { data } = await api.get<import('../types').FundingEvent[]>('/funding/events', { params: { limit } });
  return data;
}

/** Fetch aggregated funding insights. */
export async function fetchFundingInsights(): Promise<import('../types').FundingInsights> {
  const { data } = await api.get<import('../types').FundingInsights>('/funding/insights');
  return data;
}

/** Trigger tech hiring job postings ingestion. */
export async function triggerHiringIngestion(): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>('/hiring/ingest');
  return data;
}

/** Fetch recent hiring signals. */
export async function fetchHiringSignals(limit = 50): Promise<import('../types').HiringSignal[]> {
  const { data } = await api.get<import('../types').HiringSignal[]>('/hiring/signals', { params: { limit } });
  return data;
}

/** Fetch aggregated hiring insights. */
export async function fetchHiringInsights(): Promise<import('../types').HiringInsights> {
  const { data } = await api.get<import('../types').HiringInsights>('/hiring/insights');
  return data;
}

