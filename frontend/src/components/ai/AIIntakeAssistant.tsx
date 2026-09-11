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

  /* =========================
     POPULATE FORM FROM AI
     ========================= */

  const populateFormFromResult = (aiResult: any) => {
    const aiComplaint = aiResult?.complaint;

    if (!aiComplaint) {
      throw new Error("AI did not return complaint information.");
    }

    dispatch(
      populateComplaint({
        ...aiComplaint,

        initial_severity:
          aiResult.risk_assessment?.severity || "",

        priority:
          aiResult.priority_assessment?.priority || "",
      })
    );
  };

  /* =========================
     ANALYZE TEXT
     ========================= */

  const handleAnalyze = async () => {
    const complaintText = text.trim();

    if (!complaintText) {
      dispatch(
        analysisFailed(
          "Please paste a customer complaint before analyzing."
        )
      );
      return;
    }

    dispatch(analysisStarted());

    try {
      console.log("========== AI ANALYSIS ==========");
      console.log("Complaint text:", complaintText);

      const response = await analyzeComplaint(complaintText);

      console.log("AI response:", response);

      if (!response.success || !response.result) {
        throw new Error(
          "AI returned an invalid complaint analysis."
        );
      }

      dispatch(
        analysisSucceeded(response.result)
      );

      populateFormFromResult(response.result);

      setUploadedFile(null);

      console.log(
        "✓ AI analysis completed successfully."
      );
    } catch (err: unknown) {
      console.error(
        "AI ANALYSIS ERROR:",
        err
      );

      dispatch(
        analysisFailed(
          err instanceof Error
            ? err.message
            : "Unable to analyze complaint."
        )
      );
    }
  };

  /* =========================
     USE CURRENT FORM DATA
     ========================= */

  const handleUseFormData = () => {
    const formText = `
Customer Complaint

Complaint Source: ${complaint.complaint_source}

Customer Name: ${complaint.customer_name}

Product Name: ${complaint.product_name}

Product Strength / Grade: ${complaint.product_strength}

Batch / Lot Number: ${complaint.batch_number}

Manufacturing Date: ${complaint.manufacturing_date}

Expiry Date: ${complaint.expiry_date}

Quantity Affected: ${complaint.quantity_affected ?? ""}

Unit: ${complaint.quantity_unit}

Complaint Type: ${complaint.complaint_type}

Complaint Date: ${complaint.complaint_date}

Detailed Complaint Description:

${complaint.description}

Initial Severity: ${complaint.initial_severity}

Priority: ${complaint.priority}
`.trim();

    setText(formText);
    setUploadedFile(null);

    dispatch(clearAnalysis());
  };

  /* =========================
     FILE VALIDATION
     ========================= */

  const validateFile = (file: File) => {
    const extension =
      "." +
      file.name
        .split(".")
        .pop()
        ?.toLowerCase();

    if (!extension || !ALLOWED_EXTENSIONS.includes(extension)) {
      dispatch(
        analysisFailed(
          "Unsupported file format. Please upload PDF, DOCX, TXT, or EML."
        )
      );

      return false;
    }

    return true;
  };

  /* =========================
     FILE UPLOAD + AI ANALYSIS
     ========================= */

  const handleFileUpload = async (file: File) => {
    if (!validateFile(file)) {
      return;
    }

    dispatch(analysisStarted());

    setUploadedFile(file.name);

    try {
      console.log(
        "========== DOCUMENT UPLOAD =========="
      );

      console.log("File:", {
        name: file.name,
        type: file.type,
        size: file.size,
      });

      const response = await uploadComplaint(file);

      console.log(
        "Document AI response:",
        response
      );

      if (!response.success || !response.result) {
        throw new Error(
          "Document analysis returned an invalid response."
        );
      }

      dispatch(
        analysisSucceeded(response.result)
      );

      populateFormFromResult(response.result);

      /*
       * Show extracted document text
       * inside the AI textarea so the user
       * can review what was analyzed.
       */
      if (response.extracted_text) {
        setText(response.extracted_text);
      }

      console.log(
        "✓ Document processed successfully."
      );
    } catch (err: unknown) {
      console.error(
        "DOCUMENT UPLOAD ERROR:",
        err
      );

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

  /* =========================
     BROWSE FILES
     ========================= */

  const handleBrowseFiles = () => {
    fileInputRef.current?.click();
  };

  /* =========================
     FILE INPUT CHANGE
     ========================= */

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (file) {
      handleFileUpload(file);
    }

    /*
     * Reset input so the same file
     * can be selected again.
     */
    event.target.value = "";
  };

  /* =========================
     DRAG EVENTS
     ========================= */

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
      handleFileUpload(file);
    }
  };

  /* =========================
     TEXT CHANGE
     ========================= */

  const handleTextChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    setText(event.target.value);

    if (result || error) {
      dispatch(clearAnalysis());
    }

    setUploadedFile(null);
  };

  return (
    <section className="panel ai-panel">

      {/* =========================
          HEADER
          ========================= */}

      <div className="panel-header">

        <div>

          <span className="section-kicker">
            AI-POWERED INTAKE
          </span>

          <h2>
            AI Complaint Intake Assistant
          </h2>

          <p>
            Upload complaint documents or paste customer
            communication to automatically extract structured data.
          </p>

        </div>

        <span className="ai-status">
          <span className="status-dot"></span>
          AI Ready
        </span>

      </div>

      <div className="ai-divider" />

      {/* =========================
          DOCUMENT UPLOAD
          ========================= */}

      <div
        className={`upload-box ${
          isDragging
            ? "upload-dragging"
            : ""
        }`}

        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >

        <div className="upload-icon">
          ↑
        </div>

        <strong>
          {isDragging
            ? "Drop complaint document here"
            : "Drop complaint document here"}
        </strong>

        <span>
          Supported formats: PDF, DOCX, TXT, EML
        </span>

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

      {/* =========================
          UPLOADED FILE
          ========================= */}

      {uploadedFile && (
        <div className="uploaded-file">
          ✓ {uploadedFile} processed successfully
        </div>
      )}

      {/* =========================
          DIVIDER
          ========================= */}

      <div className="or-divider">
        <span>
          OR PASTE COMPLAINT TEXT
        </span>
      </div>

      {/* =========================
          TEXT INPUT
          ========================= */}

      <textarea
        className="ai-textarea"
        value={text}
        onChange={handleTextChange}
        placeholder="Paste a customer complaint or email here..."
        disabled={analyzing}
      />

      {/* =========================
          FORM DATA BUTTON
          ========================= */}

      <button
        type="button"
        className="form-data-button"
        onClick={handleUseFormData}
        disabled={analyzing}
      >
        Use Current Form Data
      </button>

      {/* =========================
          ANALYZE BUTTON
          ========================= */}

      <button
        type="button"
        className="analyze-button"
        onClick={handleAnalyze}
        disabled={
          analyzing ||
          !text.trim()
        }
      >
        {analyzing
          ? "Analyzing Complaint..."
          : "Analyze Complaint"}
      </button>

      {/* =========================
          PROGRESS
          ========================= */}

      {analyzing && (
        <div className="ai-progress">

          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>

          <span>
            AI is extracting and assessing complaint information...
          </span>

        </div>
      )}

      {/* =========================
          ERROR
          ========================= */}

      {error && !analyzing && (
        <div className="ai-error">

          <strong>
            AI analysis failed
          </strong>

          <span>
            {error}
          </span>

        </div>
      )}

      {/* =========================
          AI ASSESSMENT
          ========================= */}

      {result && !analyzing && (
        <div className="ai-assessment">

          <div className="assessment-header">

            <div>

              <span className="section-kicker">
                AI ASSESSMENT
              </span>

              <h3>
                Complaint Analysis
              </h3>

            </div>

            <span className="confidence">
              {Math.round(
                (result.risk_assessment?.confidence || 0) *
                  100
              )}
              % confidence
            </span>

          </div>

          {/* =========================
              ASSESSMENT CARDS
              ========================= */}

          <div className="assessment-grid">

            <div className="assessment-card">

              <span>
                Completeness
              </span>

              <strong>
                {result.completeness?.score ?? 0}%
              </strong>

              <small>
                {result.completeness?.status ||
                  "Unknown"}
              </small>

            </div>

            <div className="assessment-card">

              <span>
                Risk Level
              </span>

              <strong>
                {result.risk_assessment?.risk_level ||
                  "Unknown"}
              </strong>

              <small>
                {result.risk_assessment?.severity ||
                  "Unknown"}
              </small>

            </div>

            <div className="assessment-card">

              <span>
                Priority
              </span>

              <strong>
                {result.priority_assessment?.priority ||
                  "Unknown"}
              </strong>

              <small>
                AI recommended
              </small>

            </div>

          </div>

          {/* =========================
              AI REASONING
              ========================= */}

          {result.risk_assessment?.reason && (
            <div className="assessment-reason">

              <strong>
                AI Reasoning
              </strong>

              <p>
                {result.risk_assessment.reason}
              </p>

            </div>
          )}

          {/* =========================
              MISSING INFORMATION
              ========================= */}

          {result.completeness?.missing_fields?.length >
            0 && (
            <div className="missing-fields">

              <strong>
                Missing Information
              </strong>

              <ul>
                {result.completeness.missing_fields.map(
                  (field) => (
                    <li key={field}>
                      {field}
                    </li>
                  )
                )}
              </ul>

            </div>
          )}

          {/* =========================
              SUCCESS
              ========================= */}

          <div className="ai-success">
            ✓ Complaint information extracted and form populated.
          </div>

        </div>
      )}

    </section>
  );
}