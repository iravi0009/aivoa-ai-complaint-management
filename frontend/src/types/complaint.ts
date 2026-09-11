export interface Complaint {
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
}

export interface Completeness {
  score: number;
  missing_fields: string[];
  status: string;
}

export interface RiskAssessment {
  risk_level: string;
  severity: string;
  confidence: number;
  reason: string;
}

export interface PriorityAssessment {
  priority: string;
}

export interface AIAnalysisResult {
  complaint: Partial<Complaint>;
  completeness: Completeness;
  risk_assessment: RiskAssessment;
  priority_assessment: PriorityAssessment;
  errors: string[];
}

export interface AIAnalysisResponse {
  success: boolean;
  result: AIAnalysisResult;
}