import { useState } from "react";
import ComplaintForm from "./components/complaint/ComplaintForm";
import AIIntakeAssistant from "./components/ai/AIIntakeAssistant";
import ComplaintList from "./components/complaint/ComplaintList";
import ComplaintDetail from "./components/complaint/ComplaintDetail";

function App() {
  const [selectedComplaintId, setSelectedComplaintId] =
    useState<number | null>(null);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <strong>AIVOA.AI</strong>
            <span>Quality Management System</span>
          </div>
        </div>

        <div className="topbar-right">
          <span className="environment">● Development</span>
          <span className="user-avatar">RR</span>
        </div>
      </header>

      <main className="page">
        {selectedComplaintId === null ? (
          <>
            <div className="page-heading">
              <div>
                <p className="eyebrow">PHARMACEUTICAL QUALITY</p>
                <h1>Customer Complaint Management</h1>
                <p>
                  Capture, analyze and triage customer complaints
                  with AI-assisted intake.
                </p>
              </div>
            </div>

            <div className="workspace">
              <ComplaintForm />
              <AIIntakeAssistant />
            </div>

            <ComplaintList
              onViewComplaint={(id) => setSelectedComplaintId(id)}
            />
          </>
        ) : (
          <ComplaintDetail
            complaintId={selectedComplaintId}
            onBack={() => setSelectedComplaintId(null)}
          />
        )}
      </main>
    </div>
  );
}

export default App;