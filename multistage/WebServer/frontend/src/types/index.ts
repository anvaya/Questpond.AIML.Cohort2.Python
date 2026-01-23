// Type definitions for the ATS API
export type JobType = 'candidate' | 'employer';
export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface Job {
  id: string;
  type: JobType;
  status: JobStatus;
  progress: number;
  message: string;
  result?: any;
  created_at: string;
  error_message?: string;
}

export interface CandidateIdentity {
  full_name: string;
  linkedin?: string;
  github?: string;
}

export interface CandidateRole {
  title: string;
  verified_duration: number;
  raw_technologies: string[];
  domains: string[];
}

export interface CandidateProfile {
  identity: CandidateIdentity;
  candidate_roles: CandidateRole[];
}

export interface SkillBreakdown {
  skill_name: string;
  type: string; // 'Explicit' or 'Inferred'
  match_type: string; // 'Verified' or 'Unmapped'
  weight: number;
  experience_months: number;
  last_used_date: string;
  recency_score: number;
  competency_score: number;
  contribution_to_total: number;
}

export interface UnmatchedSkill {
  skill_name: string;
  type: string;
  reason: string;
}

export interface MatchCandidate {
  name: string;
  score: number;
  matches: string[];
  confidence: string;
  skill_breakdown?: SkillBreakdown[];
  unmatched_skills?: UnmatchedSkill[];
  total_jd_skills?: number;
  matched_skill_count?: number;
  unmatched_skill_count?: number;
}

export interface JobMetadata {
  primary_domain: string;
  seniority_level: string;
}

export interface EmployerResult {
  matches: MatchCandidate[];
  role_context: string | JobMetadata;
}
