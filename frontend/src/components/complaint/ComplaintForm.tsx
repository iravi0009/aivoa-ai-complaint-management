import { useDispatch, useSelector } from "react-redux";
import type { RootState, AppDispatch } from "../../app/store";

import {
  resetComplaint,
  updateField,
  submitComplaint,
} from "../../features/complaint/complaintSlice";

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
    (state: RootState) =>
      state.complaint.savedComplaintNumber
  );

  const saveError = useSelector(
    (state: RootState) => state.complaint.error
  );

  const handleSave = () => {
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

    dispatch(submitComplaint(complaint));
  };

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

        <span className="status-badge">
          Pending Triage
        </span>
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
          onClick={() => dispatch(resetComplaint())}
          disabled={saving}
        >
          Reset Form
        </button>

        <button
          type="button"
          className="button primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? "Saving Complaint..." : "Save Complaint"}
        </button>
      </div>

      {/* Success Message */}
      {saved && (
        <div className="save-success">
          ✓ Complaint saved successfully
          {savedComplaintNumber && (
            <strong>
              {" "}
              — {savedComplaintNumber}
            </strong>
          )}
        </div>
      )}

      {/* Error Message */}
      {saveError && (
        <div className="save-error">
          ✕ {saveError}
        </div>
      )}
    </div>
  );
}