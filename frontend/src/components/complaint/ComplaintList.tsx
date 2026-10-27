
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import type { RootState, AppDispatch } from "../../app/store";
import { fetchComplaints } from "../../features/complaint/complaintSlice";

interface ComplaintListProps {
  onViewComplaint: (id: number) => void;
}

export default function ComplaintList({
  onViewComplaint,
}: ComplaintListProps) {
  const dispatch = useDispatch<AppDispatch>();

  const complaints = useSelector(
    (state: RootState) => state.complaint.list
  );

  const loading = useSelector(
    (state: RootState) => state.complaint.listLoading
  );

  const error = useSelector(
    (state: RootState) => state.complaint.listError
  );

  useEffect(() => {
    dispatch(fetchComplaints());
  }, [dispatch]);

  return (
    <section className="complaint-list panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">QUALITY MANAGEMENT</p>
          <h2>Customer Complaints</h2>
          <p>
            Review submitted complaints and their current triage status.
          </p>
        </div>

        <span className="status-badge">
          {complaints.length} Records
        </span>
      </div>

      {loading && (
        <div className="list-state">Loading complaints...</div>
      )}

      {error && <div className="save-error">{error}</div>}

      {!loading && !error && complaints.length === 0 && (
        <div className="list-state">No complaints found.</div>
      )}

      {!loading && !error && complaints.length > 0 && (
        <div className="complaint-table-wrapper">
          <table className="complaint-table">
            <thead>
              <tr>
                <th>Complaint</th>
                <th>Product</th>
                <th>Type</th>
                <th>Risk</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {complaints.map((complaint) => (
                <tr key={complaint.id ?? complaint.complaint_number}>
                  <td>
                    <strong>
                      {complaint.complaint_number || `#${complaint.id}`}
                    </strong>
                  </td>

                  <td>{complaint.product_name || "—"}</td>
                  <td>{complaint.complaint_type?.trim() || "—"}</td>
                  <td>{complaint.ai_risk_level || "—"}</td>
                  <td>{complaint.priority || "—"}</td>
                  <td>{complaint.status || "—"}</td>

                  <td>
                    {complaint.created_at
                      ? new Date(
                          complaint.created_at
                        ).toLocaleDateString()
                      : "—"}
                  </td>

                  <td>
                    {typeof complaint.id === "number" ? (
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => onViewComplaint(complaint.id!)}
                      >
                        View
                      </button>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
