/**
 * types/index.ts
 * Shared TypeScript types for the Opportunity Intelligence Platform.
 */

export interface Company {
  id: string;
  name: string;
  domain: string | null;
  ats_platform: string | null;
  blog_url: string | null;
  created_at: string;
}

export interface Signal {
  id: string;
  company_id: string;
  company_name: string;
  source_type: 'career_page' | 'engineering_blog';
  event_type: string | null;
  technologies: string[];
  topics: string[];
  pain_indicators: string[];
  business_implications: string[];
  opportunity_mapping: string[];
  confidence: number;
  evidence: string[];
  source_url: string | null;
  ai_analysis: AIAnalysis | null;
  role_title: string | null;
  department: string | null;
  seniority: string | null;
  location?: string | null;
  urgency?: string;
  timestamp?: string;
  created_at: string;
}

export interface AIAnalysis {
  detected_opportunity: string;
  confidence: number;
  reasoning: string[];
  recommended_outreach: {
    stakeholder: string;
    angle: string;
  };
}

export interface AnalyzeResponse {
  company_name: string;
  ats_platform: string | null;
  ats_url: string | null;
  blog_url: string | null;
  career_signals_count: number;
  blog_signals_count: number;
  market_pain_count: number;
  total_signals: number;
  signals: Signal[];
  market_pain_signals: MarketPainSignal[];
  ai_analysis: AIAnalysis | null;
}

export interface MarketPainSignal {
  id: string;
  source: string;
  subreddit: string;
  title: string;
  body: string;
  url: string;
  upvotes: number;
  num_comments: number;
  product: string | null;
  company: string | null;
  technologies: string[];
  pain_category: string;
  pain_subcategories: string[];
  workflow_pains: string[];
  severity: string;
  sentiment_score: number;
  momentum_score: number;
  strategic_fit_score: number;
  confidence: number;
  matched_practices: string[];
  matched_accelerators: string[];
  created_at: string | null;
}

export interface GitHubIssueSignal {
  id: number;
  external_id: string;
  title: string;
  content: string;
  source_url: string;
  created_at: string | null;
  org: string | null;
  repo: string | null;
  comments: number | null;
  labels: string[];
  query: string | null;
}

export interface GitNormalizedSignal {
  id: number;
  signal_type: string;
  severity: string;
  ecosystem: string;
  confidence: number;
  title: string;
  source_url: string;
  org: string | null;
  repo: string | null;
  created_at: string | null;
}

export interface MetricCount {
  [key: string]: any;
  count: number;
}

export interface GitInsights {
  top_signal_types: { signal_type: string; count: number }[];
  ecosystem_distribution: { ecosystem: string; count: number }[];
  severity_distribution: { severity: string; count: number }[];
  top_organizations: { org: string; count: number }[];
  high_severity_organizations: { org: string; count: number }[];
}

export interface FundingEvent {
  id: string;
  company_id: string;
  company_name?: string;
  amount: number | null;
  stage: string | null;
  date: string;
  source_url: string | null;
  raw_text: string | null;
  opportunity_score: number;
}

export interface FundingInsights {
  total_funding: number;
  average_funding: number;
  events_count: number;
  stage_distribution: { stage: string; count: number }[];
  top_funded: { company_name: string; amount: number }[];
}

export interface HiringSignal {
  id: string;
  company_id: string;
  company_name?: string;
  job_title: string;
  posted_date: string | null;
  sanitized_description: string;
  detected_tech_stack: string[];
  created_at: string;
}

export interface HiringInsights {
  total_jobs: number;
  top_skills: { tech: string; count: number }[];
  top_hiring: { company_name: string; count: number }[];
}

