
import { useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import type { AppDispatch, RootState } from "../../app/store";

import {
  analysisFailed,
  analysisStarted,
  analysisSucceeded,
  clearAnalysis,
} from "../../features/ai/aiSlice";

import { populateComplaint } from "../../features/complaint/complaintSlice";

import {
  analyzeComplaint,
  uploadComplaint,
} from "../../services/api";

import type { AIAnalysisResult } from "../../types/complaint";

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".eml"];

export default function AIIntakeAssistant() {
  const dispatch = useDispatch<AppDispatch>();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [text, setText] = useState("");
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const complaint = useSelector(
    (state: RootState) => state.complaint.current
  );

  const analyzing = useSelector(
    (state: RootState) => state.ai.analyzing
  );

  const result = useSelector(
    (state: RootState) => state.ai.result
  );

  const error = useSelector(
    (state: RootState) => state.ai.error
  );

  const populateFormFromResult = (aiResult: AIAnalysisResult) => {
    if (!aiResult?.complaint) {
      throw new Error("AI did not return complaint information.");
    }

    dispatch(
      populateComplaint({
        ...aiResult.complaint,
        initial_severity: aiResult.risk_assessment?.severity || "",
        priority: aiResult.priority_assessment?.priority || "",
      })
    );
  };

  const handleAnalyze = async () => {
    const complaintText = text.trim();

    if (!complaintText) {
      dispatch(
        analysisFailed("Please paste a customer complaint before analyzing.")
      );
      return;
    }

    dispatch(analysisStarted());

    try {
      const response = await analyzeComplaint(complaintText);

      if (!response.success || !response.result) {
        throw new Error("AI returned an invalid complaint analysis.");
      }

      dispatch(analysisSucceeded(response.result));
      populateFormFromResult(response.result);
      setUploadedFile(null);
    } catch (err: unknown) {
      console.error("AI ANALYSIS ERROR:", err);

      dispatch(
        analysisFailed(
          err instanceof Error ? err.message : "Unable to analyze complaint."
        )
      );
    }
  };

  const handleUseFormData = () => {
    const formText = `
Customer Complaint

Complaint Source: ${complaint.complaint_source ?? ""}
Customer Name: ${complaint.customer_name ?? ""}
Product Name: ${complaint.product_name ?? ""}
Product Strength / Grade: ${complaint.product_strength ?? ""}
Batch / Lot Number: ${complaint.batch_number ?? ""}
Manufacturing Date: ${complaint.manufacturing_date ?? ""}
Expiry Date: ${complaint.expiry_date ?? ""}
Quantity Affected: ${complaint.quantity_affected ?? ""}
Unit: ${complaint.quantity_unit ?? ""}
Complaint Type: ${complaint.complaint_type ?? ""}
Complaint Date: ${complaint.complaint_date ?? ""}

Detailed Complaint Description:
${complaint.description ?? ""}

Initial Severity: ${complaint.initial_severity ?? ""}
Priority: ${complaint.priority ?? ""}
`.trim();

    setText(formText);
    setUploadedFile(null);
    dispatch(clearAnalysis());
  };

  const validateFile = (file: File) => {
    const extension = `.${file.name.split(".").pop()?.toLowerCase()}`;

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      dispatch(
        analysisFailed(
          "Unsupported file format. Please upload PDF, DOCX, TXT, or EML."
        )
      );
      return false;
    }

    return true;
  };

  const handleFileUpload = async (file: File) => {
    if (!validateFile(file)) return;

    dispatch(analysisStarted());
    setUploadedFile(file.name);

    try {
      const response = await uploadComplaint(file);

      if (!response.success || !response.result) {
        throw new Error("Document analysis returned an invalid response.");
      }

      dispatch(analysisSucceeded(response.result));
      populateFormFromResult(response.result);

      if (response.extracted_text) {
        setText(response.extracted_text);
      }
    } catch (err: unknown) {
      console.error("DOCUMENT UPLOAD ERROR:", err);
      setUploadedFile(null);

      dispatch(
        analysisFailed(
          err instanceof Error
            ? err.message
            : "Unable to process the uploaded complaint document."
        )
      );
    }
  };

  const handleBrowseFiles = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (file) {
      void handleFileUpload(file);
    }

    event.target.value = "";
  };

  const handleDragOver = (
    event: React.DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (
    event: React.DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (
    event: React.DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    if (file) {
      void handleFileUpload(file);
    }
  };

  const handleTextChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    setText(event.target.value);

    if (result || error) {
      dispatch(clearAnalysis());
    }

    setUploadedFile(null);
  };

  const missingFields = result?.completeness?.missing_fields ?? [];
  const isComplete = result?.completeness?.is_complete ?? false;

  return (
    <section className="panel ai-panel">
      <div className="panel-header">
        <div>
          <span className="section-kicker">AI-POWERED INTAKE</span>
          <h2>AI Complaint Intake Assistant</h2>
          <p>
            Upload complaint documents or paste customer communication to
            automatically extract structured data.
          </p>
        </div>

        <span className="ai-status">
          <span className="status-dot" />
          AI Ready
        </span>
      </div>

      <div className="ai-divider" />

      <div
        className={`upload-box ${isDragging ? "upload-dragging" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-icon" aria-hidden="true">
          ↑
        </div>

        <strong>
          {isDragging ? "Drop your complaint document here" : "Drop complaint document here"}
        </strong>

        <span>Supported formats: PDF, DOCX, TXT, EML</span>

        <button
          type="button"
          className="browse-button"
          onClick={handleBrowseFiles}
          disabled={analyzing}
        >
          Browse Files
        </button>

        <input
          ref={fileInputRef}
          id="complaint-file"
          type="file"
          accept=".pdf,.docx,.txt,.eml"
          hidden
          onChange={handleFileChange}
        />
      </div>

      {uploadedFile && (
        <div className="uploaded-file">
          {analyzing ? "Processing" : "Selected"}: {uploadedFile}
        </div>
      )}

      <div className="or-divider">
        <span>OR PASTE COMPLAINT TEXT</span>
      </div>

      <textarea
        className="ai-textarea"
        value={text}
        onChange={handleTextChange}
        placeholder="Paste a customer complaint or email here..."
        disabled={analyzing}
        rows={5}
      />

      <button
        type="button"
        className="form-data-button"
        onClick={handleUseFormData}
        disabled={analyzing}
      >
        Use Current Form Data
      </button>

      <button
        type="button"
        className="analyze-button"
        onClick={() => void handleAnalyze()}
        disabled={analyzing || !text.trim()}
      >
        {analyzing ? "Analyzing Complaint..." : "Analyze Complaint"}
      </button>

      {analyzing && (
        <div className="ai-progress" role="status">
          <div className="progress-bar">
            <div className="progress-fill" />
          </div>
          <span>
            AI is extracting and assessing complaint information...
          </span>
        </div>
      )}

      {error && !analyzing && (
        <div className="ai-error" role="alert">
          <strong>AI analysis failed</strong>
          <span>{error}</span>
        </div>
      )}

      {result && !analyzing && (
        <div className="ai-assessment">
          <div className="assessment-header">
            <div>
              <span className="section-kicker">AI ASSESSMENT</span>
              <h3>Complaint Analysis</h3>
            </div>

            <span className="confidence">
              {Math.round((result.risk_assessment?.confidence ?? 0) * 100)}%
              confidence
            </span>
          </div>

          <div className="assessment-grid">
            <div className="assessment-card">
              <span>Completeness</span>
              <strong>{isComplete ? "Complete" : "Incomplete"}</strong>
              <small>
                {missingFields.length} missing{" "}
                {missingFields.length === 1 ? "field" : "fields"}
              </small>
            </div>

            <div className="assessment-card">
              <span>Risk Level</span>
              <strong>
                {result.risk_assessment?.risk_level ?? "Unknown"}
              </strong>
              <small>
                {result.risk_assessment?.severity ?? "Not assessed"}
              </small>
            </div>

            <div className="assessment-card">
              <span>Priority</span>
              <strong>
                {result.priority_assessment?.priority ?? "Unknown"}
              </strong>
              <small>AI recommended</small>
            </div>
          </div>

          {result.risk_assessment?.reasoning && (
            <div className="assessment-reason">
              <strong>AI Reasoning</strong>
              <p>{result.risk_assessment.reasoning}</p>
            </div>
          )}

          {missingFields.length > 0 && (
            <div className="missing-fields">
              <strong>Missing Information</strong>
              <ul>
                {missingFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
            </div>
          )}

          {result.completeness?.warnings &&
            result.completeness.warnings.length > 0 && (
              <div className="missing-fields">
                <strong>Review Warnings</strong>
                <ul>
                  {result.completeness.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}

          <div className="ai-success" role="status">
            ✓ Complaint information extracted and form populated.
          </div>

          <p className="ai-disclaimer">
            AI-generated assessment is decision support only. Authorized QA
            personnel must review the extracted information, risk, and priority.
          </p>
        </div>
      )}
    </section>
  );
}
