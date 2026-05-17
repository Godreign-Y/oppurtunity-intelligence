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
  opportunity_category: string | null;
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
  git_issues_count?: number;
  funding_count?: number;
  hiring_count?: number;
  total_signals: number;
  signals: Signal[];
  market_pain_signals: MarketPainSignal[];
  git_signals?: any[];
  funding_signals?: any[];
  hiring_signals?: any[];
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
  opportunity_category: string | null;
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
  opportunity_category?: string | null;
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
  opportunity_category?: string | null;
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
  opportunity_category?: string | null;
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
  source_url?: string | null;
  opportunity_category?: string | null;
  created_at: string;
}

export interface HiringInsights {
  total_jobs: number;
  top_skills: { tech: string; count: number }[];
  top_hiring: { company_name: string; count: number }[];
}

export interface PipelineRun {
  id: string;
  company_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  pipelines_selected: string[];
  results: AnalyzeResponse | null;
  errors: Record<string, string> | null;
  created_at: string;
  updated_at: string;
}

export interface RelantoPractice {
  practice_name: string;
  practice_code: string;
  practice_category: string | null;
  description: string | null;
  relevance_score?: number;
  delivery_strength: number | null;
  sme_count: number | null;
  growth_priority: boolean;
}

export interface RelantoPastDeal {
  client_name: string | null;
  project_name: string | null;
  technologies_used: string[];
  transformation_outcome: string | null;
  client_satisfaction_score: number | null;
}

export interface RelantoOpportunity {
  id: string;
  company_name: string;
  source: string;
  title: string;
  body: string | null;
  source_url: string | null;
  opportunity_category: string;
  confidence: number;
  technologies: string[];
  pain_indicators: string[];
  score: number;
  priority: 'High' | 'Medium' | 'Low';
  relanto_relevance_score: number;
  practices: RelantoPractice[];
  past_deals: RelantoPastDeal[];
  reason: string;
}

export interface DecisionMaker {
  first_name: string | null;
  last_name: string | null;
  title: string | null;
  email: string | null;
  linkedin_url: string | null;
  confidence: number | null;
  source: string;
}

export interface OutreachRecommendation {
  opportunity_id: string;
  company_name: string;
  opportunity: string;
  source: string;
  score: number;
  relanto_relevance_score: number;
  priority: 'High' | 'Medium' | 'Low';
  practices: RelantoPractice[];
  suggested_personas: string[];
  decision_makers: DecisionMaker[];
  source_url: string | null;
  angle: string;
}

