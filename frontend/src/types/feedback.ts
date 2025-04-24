export enum MatchQualityEnum {
  VERY_GOOD = "très bon",
  GOOD = "bon",
  MEDIUM = "moyen",
  POOR = "faible",
  UNACCEPTABLE = "inacceptable"
}

export interface Feedback {
  id: string;
  match_id: string;
  user_id: string;
  user_type: "recruiter" | "candidate";
  rating: number;
  match_quality: MatchQualityEnum;
  comment?: string;
  algorithm_version: string;
  created_at: string;
  updated_at: string;
}

export interface FeedbackStats {
  average_rating: number;
  total_feedbacks: number;
  quality_distribution: Record<MatchQualityEnum, number>;
  latest_feedback_date: string | null;
}

export interface FeedbackFilters {
  algorithm_version?: string;
  min_rating?: number;
  max_rating?: number;
  start_date?: string;
  end_date?: string;
  user_type?: "recruiter" | "candidate";
}