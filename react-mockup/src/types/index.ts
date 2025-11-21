export interface Question {
  questionid: number;
  worksheet_id: string;           // e.g., "S09TISNID12"
  question: string;               // HTML with <p>, <ol>, etc.
  questionImage?: string;         // Filename or null
  answer1: string;
  answer1Image?: string;
  answer2: string;
  answer2Image?: string;
  answer3: string;
  answer3Image?: string;
  answer4: string;
  answer4Image?: string;
  answer5?: string;
  answer5Image?: string;
  correctanswer: string;          // 'a', 'b', 'c', 'd', 'e'
  hint?: string;
  topic?: string;

  // AI Processing fields (added by LLM)
  ai_question_rewrite?: string;
  ai_question_reason?: string;
  ai_answer1_rewrite?: string;
  ai_answer1_reason?: string;
  ai_answer2_rewrite?: string;
  ai_answer2_reason?: string;
  ai_answer3_rewrite?: string;
  ai_answer3_reason?: string;
  ai_answer4_rewrite?: string;
  ai_answer4_reason?: string;
  ai_answer5_rewrite?: string;
  ai_answer5_reason?: string;

  // Review fields (added by human)
  review_status?: 'pending' | 'approved' | 'rejected';
  review_classification?: 'all_ok' | 'mistake' | 'hallucinated' | 'other';
  final_question?: string;
  final_answer1?: string;
  final_answer2?: string;
  final_answer3?: string;
  final_answer4?: string;
  final_answer5?: string;

  // Metadata
  ai_processed: boolean;
  human_reviewed: boolean;
}

export type NavItem = 'review' | 'llm' | 'batch';

export interface DashboardMetrics {
  api_calls: {
    total: number;
    successful: number;
    failed: number;
  };
  questions: {
    total: number;
    processed: number;
    changes_recommended: number;
    change_rate_percent: number;
  };
  tokens: {
    input_total: number;
    output_total: number;
    reasoning_total: number;
  };
  cost: {
    total_usd: number;
    per_question_usd: number;
    per_100k_usd: number;
  };
  time: {
    total_seconds: number;
    per_question_seconds: number;
    per_api_call_seconds: number;
  };
}
