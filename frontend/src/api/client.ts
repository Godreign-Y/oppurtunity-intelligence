/**
 * api/client.ts
 * Axios-based API client for the Opportunity Intelligence Platform backend.
 *
 * In development: uses Vite's dev proxy (/api → http://127.0.0.1:8000)
 * In production:  uses VITE_API_BASE_URL env variable (e.g. https://api.yourdomain.com)
 */

import axios from 'axios';
import type { Company, Signal } from '../types';

const _apiBase = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
  : '/api/v1';

const api = axios.create({
  baseURL: _apiBase,
  headers: { 'Content-Type': 'application/json' },
});

/** Trigger the full analysis pipeline for a company. */
export async function startAnalyzeCompany(companyName: string, pipelines: string[]): Promise<import('../types').PipelineRun> {
  const { data } = await api.post<import('../types').PipelineRun>('/analyze/start', {
    company_name: companyName,
    pipelines_selected: pipelines
  });
  return data;
}

export async function getPipelineRuns(companyName: string): Promise<import('../types').PipelineRun[]> {
  const { data } = await api.get<import('../types').PipelineRun[]>(`/analyze/runs/${encodeURIComponent(companyName)}`);
  return data;
}

export async function getPipelineRun(runId: string): Promise<import('../types').PipelineRun> {
  const { data } = await api.get<import('../types').PipelineRun>(`/analyze/${runId}`);
  return data;
}

export async function fetchPipelineLogs(params?: { runId?: string; companyName?: string; limit?: number }): Promise<string[]> {
  const { data } = await api.get<{ lines: string[] }>('/analyze/logs/tail', {
    params: {
      run_id: params?.runId,
      company_name: params?.companyName,
      limit: params?.limit ?? 120,
    },
  });
  return data.lines;
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

export async function fetchRelantoPractices(): Promise<import('../types').RelantoPractice[]> {
  const { data } = await api.get<import('../types').RelantoPractice[]>('/service-intelligence/practices');
  return data;
}

export async function fetchRelantoOpportunities(companyName?: string, practiceCode?: string, refresh = false): Promise<import('../types').RelantoOpportunity[]> {
  const { data } = await api.get<import('../types').RelantoOpportunity[]>('/service-intelligence/opportunities', {
    params: { company_name: companyName || undefined, practice_code: practiceCode || undefined, refresh },
  });
  return data;
}

export async function fetchOutreachRecommendations(companyName?: string): Promise<import('../types').OutreachRecommendation[]> {
  const { data } = await api.get<import('../types').OutreachRecommendation[]>('/outreach/recommendations', {
    params: { company_name: companyName || undefined },
  });
  return data;
}
