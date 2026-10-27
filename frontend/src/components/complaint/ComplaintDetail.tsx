
import { useEffect, useState } from "react";
import {
  getComplaint,
  getInvestigation,
  createInvestigation,
  updateInvestigation,
  recommendRootCauses,
  recommendCAPA,
} from "../../services/api";
import type {
  Complaint,
  Investigation,
  RootCauseRecommendation,
  CAPARecommendation,
} from "../../types/complaint";

interface ComplaintDetailProps {
  complaintId: number;
  onBack: () => void;
}

export default function ComplaintDetail({
  complaintId,
  onBack,
}: ComplaintDetailProps) {
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);
  const [summary, setSummary] = useState("");
  const [impact, setImpact] = useState("");
  const [rootCause, setRootCause] = useState("");
  const [conclusion, setConclusion] = useState("");
  const [rootRecommendations, setRootRecommendations] =
    useState<RootCauseRecommendation | null>(null);
  const [capa, setCapa] = useState<CAPARecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const record = await getComplaint(complaintId);
      setComplaint(record);

      try {
        const existing = await getInvestigation(complaintId);
        setInvestigation(existing);
        setSummary(existing.investigation_summary ?? "");
        setImpact(existing.impact_assessment ?? "");
        setRootCause(existing.root_cause ?? "");
        setConclusion(existing.conclusion ?? "");
      } catch {
        // No investigation may exist yet.
        setInvestigation(null);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load complaint details."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [complaintId]);

  async function saveInvestigation() {
    setSaving(true);
    setError("");
    setMessage("");

    const payload = {
      investigation_summary: summary,
      impact_assessment: impact,
      root_cause: rootCause,
      conclusion,
    };

    try {
      const result = investigation
        ? await updateInvestigation(complaintId, payload)
        : await createInvestigation(complaintId, payload);

      setInvestigation(result);
      setMessage("Investigation saved successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to save investigation."
      );
    } finally {
      setSaving(false);
    }
  }

  async function changeStatus(status: string) {
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const result = investigation
        ? await updateInvestigation(complaintId, { status })
        : await createInvestigation(complaintId, {});

      if (investigation) {
        setInvestigation(result);
      } else {
        setInvestigation(result);
      }

      setMessage(`Investigation status updated to ${status}.`);
      await loadData();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update investigation status."
      );
    } finally {
      setSaving(false);
    }
  }

  async function generateRootCauses() {
    setAiLoading(true);
    setError("");
    setRootRecommendations(null);

    try {
      const result = await recommendRootCauses(complaintId);
      setRootRecommendations(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate root-cause recommendations."
      );
    } finally {
      setAiLoading(false);
    }
  }

  async function generateCAPA() {
    setAiLoading(true);
    setError("");
    setCapa(null);

    try {
      const result = await recommendCAPA(complaintId);
      setCapa(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate CAPA recommendations."
      );
    } finally {
      setAiLoading(false);
    }
  }

  if (loading) {
    return <section className="panel">Loading complaint details...</section>;
  }

  if (!complaint) {
    return (
      <section className="panel">
        <button className="button secondary" onClick={onBack}>
          Back to complaints
        </button>
        <p className="save-error">{error || "Complaint not found."}</p>
      </section>
    );
  }

  return (
    <section className="complaint-detail">
      <button className="button secondary" onClick={onBack}>
        ← Back to complaints
      </button>

      <section className="panel detail-header">
        <div>
          <p className="eyebrow">COMPLAINT INVESTIGATION</p>
          <h2>{complaint.complaint_number || `Complaint #${complaintId}`}</h2>
          <p>
            {complaint.product_name || "Product not specified"} ·{" "}
            {complaint.batch_number || "Batch not specified"}
          </p>
        </div>

        <div className="detail-badges">
          <span className="status-badge">
            {complaint.status || "Pending Triage"}
          </span>
          <span className="status-badge">
            Risk: {complaint.ai_risk_level || "Not assessed"}
          </span>
          <span className="status-badge">
            Priority: {complaint.priority || "Not assigned"}
          </span>
        </div>
      </section>

      {error && <div className="save-error">{error}</div>}
      {message && <div className="save-success">{message}</div>}

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">COMPLAINT RECORD</p>
            <h2>Complaint Information</h2>
          </div>
        </div>

        <div className="detail-grid">
          <Detail label="Customer" value={complaint.customer_name} />
          <Detail label="Source" value={complaint.complaint_source} />
          <Detail label="Product" value={complaint.product_name} />
          <Detail label="Strength / Grade" value={complaint.product_strength} />
          <Detail label="Batch / Lot" value={complaint.batch_number} />
          <Detail label="Complaint Type" value={complaint.complaint_type} />
          <Detail label="Complaint Date" value={complaint.complaint_date} />
          <Detail label="Initial Severity" value={complaint.initial_severity} />
          <div className="detail-field detail-field-full">
            <strong>Description</strong>
            <p>{complaint.description || "No description recorded."}</p>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">QUALITY INVESTIGATION</p>
            <h2>Investigation Workspace</h2>
          </div>
          <span className="status-badge">
            {investigation?.status || "Not started"}
          </span>
        </div>

        <label className="field">
          <span>Investigation Summary</span>
          <textarea
            rows={3}
            value={summary}
            onChange={(event) => setSummary(event.target.value)}
            placeholder="Record investigation activities and evidence..."
          />
        </label>

        <label className="field">
          <span>Impact Assessment</span>
          <textarea
            rows={3}
            value={impact}
            onChange={(event) => setImpact(event.target.value)}
            placeholder="Document the assessed product, batch, and patient impact..."
          />
        </label>

        <label className="field">
          <span>Root Cause (QA-confirmed)</span>
          <textarea
            rows={3}
            value={rootCause}
            onChange={(event) => setRootCause(event.target.value)}
            placeholder="Enter the confirmed root cause only after investigation..."
          />
        </label>

        <label className="field">
          <span>Conclusion</span>
          <textarea
            rows={3}
            value={conclusion}
            onChange={(event) => setConclusion(event.target.value)}
            placeholder="Record the investigation conclusion..."
          />
        </label>

        <div className="form-actions">
          <button
            className="button primary"
            onClick={saveInvestigation}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Investigation"}
          </button>

          <button
            className="button secondary"
            onClick={() => void changeStatus("UNDER_INVESTIGATION")}
            disabled={saving}
          >
            Start Investigation
          </button>

          <button
            className="button secondary"
            onClick={() => void changeStatus("COMPLETED")}
            disabled={saving}
          >
            Mark Investigation Complete
          </button>
        </div>
      </section>

      <section className="panel">
        <p className="eyebrow">AI-ASSISTED QUALITY TOOLS</p>
        <h2>Root Cause Recommendations</h2>
        <p>
          AI suggestions support investigation planning; they do not establish
          a confirmed root cause.
        </p>

        <button
          className="button primary"
          onClick={() => void generateRootCauses()}
          disabled={aiLoading}
        >
          {aiLoading ? "Generating..." : "Generate Root Cause Recommendations"}
        </button>

        {rootRecommendations && (
          <div className="recommendation-content">
            <h3>Suggested Investigation Activities</h3>
            <ul>
              {rootRecommendations.recommendations.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
            <p>{rootRecommendations.rationale}</p>
            <p className="disclaimer">{rootRecommendations.disclaimer}</p>
          </div>
        )}
      </section>

      <section className="panel">
        <p className="eyebrow">CORRECTIVE & PREVENTIVE ACTIONS</p>
        <h2>CAPA Recommendations</h2>
        <p>
          Recommendations must be evaluated against investigation evidence
          and approved through the site's quality system.
        </p>

        <button
          className="button primary"
          onClick={() => void generateCAPA()}
          disabled={aiLoading}
        >
          {aiLoading ? "Generating..." : "Generate CAPA Recommendations"}
        </button>

        {capa && (
          <div className="recommendation-content">
            <h3>Corrective Actions</h3>
            <ul>
              {capa.corrective_actions.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>

            <h3>Preventive Actions</h3>
            <ul>
              {capa.preventive_actions.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>

            <p>{capa.rationale}</p>
            <p className="disclaimer">{capa.disclaimer}</p>
          </div>
        )}
      </section>

      <p className="disclaimer">
        AI-generated content is decision support only. Authorized Quality
        Assurance personnel must review and approve investigation conclusions,
        risk decisions, and CAPA actions.
      </p>
    </section>
  );
}

function Detail({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="detail-field">
      <strong>{label}</strong>
      <p>{value || "—"}</p>
    </div>
  );
}
