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
  total_signals: number;
  signals: Signal[];
  ai_analysis: AIAnalysis | null;
}
