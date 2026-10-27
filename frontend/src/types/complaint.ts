/* =========================
   COMPLAINT
   ========================= */

export interface Complaint {
  /* Database / response fields */
  id?: number;
  complaint_number?: string;
  status?: string;
  ai_risk_level?: string;
  created_at?: string;
  updated_at?: string;

  /* Complaint fields */
  complaint_source: string;
  customer_name: string;
  product_name: string;
  product_strength: string;
  batch_number: string;
  manufacturing_date: string;
  expiry_date: string;
  quantity_affected: number | null;
  quantity_unit: string;
  complaint_type: string;
  complaint_date: string;
  description: string;
  initial_severity: string;
  priority: string;

  /* AI confidence */
  ai_confidence?: number | null;
}

/* =========================
   AI COMPLETENESS
   ========================= */

export interface Completeness {
  score?: number;
  is_complete?: boolean;
  missing_fields: string[];
  status?: string;
  warnings?: string[];
}

/* =========================
   AI RISK ASSESSMENT
   ========================= */

export interface RiskAssessment {
  risk_level: string;
  severity: string;
  confidence: number;
  reason?: string;
  reasoning?: string;
  score?: number;
  factors?: string[];
}

/* =========================
   AI PRIORITY ASSESSMENT
   ========================= */

export interface PriorityAssessment {
  priority: string;
  reasoning?: string;
}

/* =========================
   AI ANALYSIS RESULT
   ========================= */

export interface AIAnalysisResult {
  complaint: Partial<Complaint>;
  completeness: Completeness;
  risk_assessment: RiskAssessment;
  priority_assessment: PriorityAssessment;
  errors: string[];
}

/* =========================
   AI ANALYSIS RESPONSE
   ========================= */

export interface AIAnalysisResponse {
  success: boolean;
  result: AIAnalysisResult;
}

/* =========================
   INVESTIGATION
   ========================= */

export interface Investigation {
  id: number;
  complaint_id: number;
  status: string;
  investigation_summary: string | null;
  impact_assessment: string | null;
  root_cause: string | null;
  conclusion: string | null;
  created_at: string;
  updated_at: string;
}

/* =========================
   ROOT CAUSE RECOMMENDATION
   ========================= */

export interface RootCauseRecommendation {
  recommendations: string[];
  rationale: string;
  disclaimer: string;
}

/* =========================
   CAPA RECOMMENDATION
   ========================= */

export interface CAPARecommendation {
  corrective_actions: string[];
  preventive_actions: string[];
  rationale: string;
  disclaimer: string;
}