
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { RootState, AppDispatch } from "../../app/store";

import {
  resetComplaint,
  updateField,
  submitComplaint,
} from "../../features/complaint/complaintSlice";

import {
  checkDuplicate,
  type DuplicateCheckResult,
} from "../../services/api";

import FormSection from "./FormSection";

function Field({
  label,
  field,
  type = "text",
  placeholder = "",
}: {
  label: string;
  field: keyof RootState["complaint"]["current"];
  type?: string;
  placeholder?: string;
}) {
  const dispatch = useDispatch<AppDispatch>();

  const value = useSelector(
    (state: RootState) => state.complaint.current[field]
  );

  return (
    <label className="field">
      <span>{label}</span>

      <input
        type={type}
        value={value ?? ""}
        placeholder={placeholder}
        onChange={(event) =>
          dispatch(
            updateField({
              field,
              value:
                type === "number"
                  ? event.target.value
                    ? Number(event.target.value)
                    : null
                  : event.target.value,
            })
          )
        }
      />
    </label>
  );
}

export default function ComplaintForm() {
  const dispatch = useDispatch<AppDispatch>();

  const complaint = useSelector(
    (state: RootState) => state.complaint.current
  );

  const saving = useSelector(
    (state: RootState) => state.complaint.saving
  );

  const saved = useSelector(
    (state: RootState) => state.complaint.saved
  );

  const savedComplaintNumber = useSelector(
    (state: RootState) => state.complaint.savedComplaintNumber
  );

  const saveError = useSelector(
    (state: RootState) => state.complaint.error
  );

  const [checkingDuplicate, setCheckingDuplicate] = useState(false);
  const [duplicateError, setDuplicateError] = useState<string | null>(null);
  const [duplicateResult, setDuplicateResult] =
    useState<DuplicateCheckResult | null>(null);
  const [duplicateReviewFor, setDuplicateReviewFor] =
    useState<string | null>(null);

  const handleSave = async () => {
    if (!complaint.customer_name.trim()) {
      alert("Please enter the customer name.");
      return;
    }

    if (!complaint.product_name.trim()) {
      alert("Please enter the product name.");
      return;
    }

    if (!complaint.batch_number.trim()) {
      alert("Please enter the batch / lot number.");
      return;
    }

    if (!complaint.complaint_type.trim()) {
      alert("Please enter the complaint type.");
      return;
    }

    if (!complaint.complaint_date) {
      alert("Please enter the complaint date.");
      return;
    }

    if (!complaint.description.trim()) {
      alert("Please enter the complaint description.");
      return;
    }

    const currentComplaint = JSON.stringify(complaint);

    // Continue only after explicit confirmation.
    if (
      duplicateReviewFor === currentComplaint &&
      duplicateResult?.is_duplicate
    ) {
      setDuplicateResult(null);
      setDuplicateReviewFor(null);
      setDuplicateError(null);
      dispatch(submitComplaint(complaint));
      return;
    }

    setCheckingDuplicate(true);
    setDuplicateError(null);
    setDuplicateResult(null);
    setDuplicateReviewFor(null);

    try {
      const result = await checkDuplicate(complaint);

      if (result.is_duplicate) {
        setDuplicateResult(result);
        setDuplicateReviewFor(currentComplaint);
        return;
      }

      dispatch(submitComplaint(complaint));
    } catch (error) {
      console.error("Duplicate check failed:", error);
      setDuplicateError(
        "Could not check for duplicates. Please try again before saving."
      );
    } finally {
      setCheckingDuplicate(false);
    }
  };

const cancelDuplicateReview = () => {
  console.log("Cancel duplicate review clicked");
  console.log("Complaint before cancel:", complaint);

  setDuplicateResult(null);
  setDuplicateReviewFor(null);
  setDuplicateError(null);

  console.log("Cancel handler does not reset complaint state");
};

  const isBusy = saving || checkingDuplicate;

  return (
    <div className="panel complaint-panel">
      {/* Header */}
      <div className="panel-header">
        <div>
          <p className="eyebrow">CUSTOMER QUALITY</p>
          <h2>Log Customer Complaint</h2>
          <p>
            Capture complaint information for quality review and
            investigation.
          </p>
        </div>

        <span className="status-badge">Pending Triage</span>
      </div>

      {/* Origin & Customer */}
      <FormSection title="ORIGIN & CUSTOMER DETAILS">
        <Field
          label="Complaint Source"
          field="complaint_source"
          placeholder="Customer Email"
        />

        <Field
          label="Customer Name"
          field="customer_name"
          placeholder="Enter customer name"
        />
      </FormSection>

      {/* Product & Batch */}
      <FormSection title="PRODUCT & BATCH IDENTIFICATION">
        <Field
          label="Product Name"
          field="product_name"
          placeholder="Enter product name"
        />

        <Field
          label="Product Strength / Grade"
          field="product_strength"
          placeholder="e.g. 500 mg"
        />

        <Field
          label="Batch / Lot Number"
          field="batch_number"
          placeholder="Enter batch number"
        />

        <Field
          label="Manufacturing Date"
          field="manufacturing_date"
          type="date"
        />

        <Field
          label="Expiry Date"
          field="expiry_date"
          type="date"
        />

        <Field
          label="Quantity Affected"
          field="quantity_affected"
          type="number"
          placeholder="0"
        />

        <Field
          label="Unit"
          field="quantity_unit"
          placeholder="kg / units / packs"
        />
      </FormSection>

      {/* Complaint Details */}
      <FormSection title="COMPLAINT DETAILS">
        <Field
          label="Complaint Type"
          field="complaint_type"
          placeholder="Product Quality"
        />

        <Field
          label="Complaint Date"
          field="complaint_date"
          type="date"
        />

        <label className="field field-full">
          <span>Detailed Complaint Description</span>

          <textarea
            rows={6}
            value={complaint.description}
            placeholder="Enter detailed complaint description..."
            onChange={(event) =>
              dispatch(
                updateField({
                  field: "description",
                  value: event.target.value,
                })
              )
            }
          />
        </label>
      </FormSection>

      {/* Assessment */}
      <FormSection title="INITIAL ASSESSMENT & PRIORITY">
        <Field
          label="Initial Severity"
          field="initial_severity"
          placeholder="AI / QA assessment"
        />

        <Field
          label="Priority"
          field="priority"
          placeholder="AI / QA priority"
        />
      </FormSection>

      {/* Actions */}
      <div className="form-actions">
        <button
          type="button"
          className="button secondary"
          onClick={() => {
            dispatch(resetComplaint());
            cancelDuplicateReview();
          }}
          disabled={isBusy}
        >
          Reset Form
        </button>

        <button
          type="button"
          className="button primary"
          onClick={handleSave}
          disabled={isBusy}
        >
          {saving
            ? "Saving Complaint..."
            : checkingDuplicate
              ? "Checking Duplicates..."
              : "Save Complaint"}
        </button>
      </div>

      {/* Duplicate Warning */}
      {duplicateResult?.is_duplicate &&
        duplicateReviewFor === JSON.stringify(complaint) && (
          <div className="save-error" role="alert">
            <h3>Potential Duplicate Complaint</h3>

            <p>
              Similar complaints were found. Review the matches before
              continuing.
            </p>

            <p>
              Status: <strong>{duplicateResult.duplicate_status}</strong>
            </p>

            {duplicateResult.matches.map((match, index) => (
              <div key={`${match.complaint_id}-${index}`}>
                <p>
                  <strong>
                    Complaint:{" "}
                    {match.complaint_number ?? match.complaint_id}
                  </strong>
                </p>

                {match.score !== undefined && (
                  <p>Duplicate score: {match.score}</p>
                )}

                {match.reasons && match.reasons.length > 0 && (
                  <ul>
                    {match.reasons.map((reason, reasonIndex) => (
                      <li key={reasonIndex}>{reason}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}

            <div className="form-actions">
              <button
                type="button"
                className="button primary"
                disabled={isBusy}
                onClick={handleSave}
              >
                Continue Anyway
              </button>

              <button
                type="button"
                className="button secondary"
                onClick={cancelDuplicateReview}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

      {/* Duplicate Check Error */}
      {duplicateError && (
        <div className="save-error" role="alert">
          {duplicateError}
        </div>
      )}

      {/* Success Message */}
      {saved && (
        <div className="save-success">
          ✓ Complaint saved successfully
          {savedComplaintNumber && (
            <strong> — {savedComplaintNumber}</strong>
          )}
        </div>
      )}

      {/* Save Error */}
      {saveError && (
        <div className="save-error">
          ✕ {saveError}
        </div>
      )}
    </div>
  );
}
