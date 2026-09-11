import ComplaintForm from "./components/complaint/ComplaintForm";
import AIIntakeAssistant from "./components/ai/AIIntakeAssistant";

function App() {
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
          <span className="environment">
            ● Development
          </span>

          <span className="user-avatar">
            RR
          </span>
        </div>
      </header>

      <main className="page">
        <div className="page-heading">
          <div>
            <p className="eyebrow">
              PHARMACEUTICAL QUALITY
            </p>

            <h1>
              Customer Complaint Management
            </h1>

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
      </main>
    </div>
  );
}

export default App;