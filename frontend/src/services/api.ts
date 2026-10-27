import axios from "axios";

import type {
  AIAnalysisResponse,
  Complaint,
} from "../types/complaint";

/* =========================
   API CONFIGURATION
   ========================= */

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

console.log("AIVOA API:", API_BASE_URL);

/* =========================
   AI TEXT ANALYSIS
   ========================= */

export async function analyzeComplaint(
  text: string
): Promise<AIAnalysisResponse> {
  console.log("AI REQUEST:", text);

  const response = await api.post<AIAnalysisResponse>(
    "/api/ai/analyze",
    {
      text,
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  console.log("AI RESPONSE:", response.data);

  return response.data;
}

/* =========================
   AI DOCUMENT UPLOAD
   ========================= */

export async function uploadComplaint(
  file: File
): Promise<AIAnalysisResponse & {
  filename: string;
  file_type: string;
  extracted_text: string;
}> {
  const formData = new FormData();

  formData.append("file", file);

  console.log("UPLOAD REQUEST:", {
    name: file.name,
    type: file.type,
    size: file.size,
  });

  const response = await api.post(
    "/api/ai/upload",
    formData,
    {
      // Do NOT manually set Content-Type.
      // Axios/browser will create the multipart boundary.
      timeout: 120000,
    }
  );

  console.log("UPLOAD RESPONSE:", response.data);

  return response.data;
}

/* =========================
   SAVE COMPLAINT
   ========================= */

export async function saveComplaint(
  complaint: Complaint
) {
  console.log(
    "SAVE REQUEST:",
    `${API_BASE_URL}/api/complaints`
  );

  console.log(
    "SAVE PAYLOAD:",
    complaint
  );

  const response = await api.post(
    "/api/complaints",
    complaint,
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  console.log(
    "SAVE RESPONSE:",
    response.data
  );

  return response.data;
}


/* =========================
   DUPLICATE DETECTION
   ========================= */

export interface DuplicateMatch {
  complaint_id: number;
  complaint_number?: string;
  score?: number;
  reasons?: string[];
}

export interface DuplicateCheckResult {
  is_duplicate: boolean;
  duplicate_status:
    | "NO_DUPLICATE"
    | "POTENTIAL_DUPLICATE"
    | "HIGH_CONFIDENCE_DUPLICATE";
  matches: DuplicateMatch[];
}


export async function checkDuplicate(complaint: Complaint) {
  const payload = {
    ...complaint,
    manufacturing_date: complaint.manufacturing_date || null,
    expiry_date: complaint.expiry_date || null,
  };

  const response = await api.post<DuplicateCheckResult>(
    "/api/complaints/check-duplicate",
    payload
  );

  return response.data;
}


/* =========================
   GET COMPLAINTS
   ========================= */

export async function getComplaints() {
  const response = await api.get(
    "/api/complaints"
  );

  return response.data;
}

/* =========================
   COMPLAINT DETAIL
   ========================= */

export async function getComplaint(id: number): Promise<Complaint> {
  const response = await api.get<Complaint>(`/api/complaints/${id}`);
  return response.data;
}

/* =========================
   INVESTIGATION
   ========================= */

export async function getInvestigation(id: number) {
  const response = await api.get(
    `/api/complaints/${id}/investigation`
  );

  return response.data;
}

export async function createInvestigation(
  id: number,
  data: {
    investigation_summary?: string;
    impact_assessment?: string;
    root_cause?: string;
    conclusion?: string;
  }
) {
  const response = await api.post(
    `/api/complaints/${id}/investigation`,
    data
  );

  return response.data;
}

export async function updateInvestigation(
  id: number,
  data: {
    status?: string;
    investigation_summary?: string;
    impact_assessment?: string;
    root_cause?: string;
    conclusion?: string;
  }
) {
  const response = await api.patch(
    `/api/complaints/${id}/investigation`,
    data
  );

  return response.data;
}

/* =========================
   AI ROOT CAUSE
   ========================= */

export async function recommendRootCauses(id: number) {
  const response = await api.post(
    `/api/complaints/${id}/investigation/root-cause-recommendation`
  );

  return response.data;
}

/* =========================
   AI CAPA
   ========================= */

export async function recommendCAPA(id: number) {
  const response = await api.post(
    `/api/complaints/${id}/investigation/capa-recommendation`
  );

  return response.data;
}

export default api;