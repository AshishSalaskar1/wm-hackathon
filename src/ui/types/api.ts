/** TypeScript mirrors of the FastAPI Pydantic models defined in src/api/main.py. */

export interface DemandRecord {
  demand_id: number;
  customer_name: string;
  essential_skill: string;
  location: string;
  country: string;
  created_on: string; // ISO date string
  start_date: string;
  end_date: string;
  role_description: string;
  work_mode: "ONSITE" | "OFFSHORE";
  band: string;
  open_positions: number;
  job_description: string;
  role_cluster: string;
}

export interface MatchResult {
  rank: number;
  employee_id: string;
  employee_name: string;
  similarity_score: number;
  band: string;
  location: string;
  experience: string;
  role_name: string | null;
  skills_iaspire: string | null;
  certified_skills: string | null;
  role_cluster: string | null;
  work_mode: "ONSITE" | "OFFSHORE";
  below_threshold: boolean;
}

export type MatchStatus = "READY" | "MATCHING_IN_PROGRESS" | "NO_RESULTS";

export interface MatchResultsResponse {
  demand_id: number;
  status: MatchStatus;
  page: number;
  has_more: boolean;
  results: MatchResult[];
}

export interface HealthResponse {
  status: string;
}
