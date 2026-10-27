# AIVOA.AI — AI-Powered Pharmaceutical Complaint Management System

An AI-assisted pharmaceutical quality management prototype for capturing, analyzing, tracking, and investigating product complaints.

**Repository:** [aivoa-ai-complaint-management](https://github.com/iravi0009/aivoa-ai-complaint-management)

---

## Overview

AIVOA.AI is a full-stack application designed to streamline pharmaceutical complaint handling with AI-assisted data extraction, completeness checks, risk assessment, duplicate detection, and investigation support.

The application combines a React and TypeScript frontend with a Python FastAPI backend and LangGraph-based AI workflows. It helps quality teams organize complaint information and generate preliminary recommendations for further review.

> **Important:** This project is a prototype for demonstration and development purposes. It is not validated GxP software. AI-generated classifications and recommendations must be reviewed by qualified personnel before any real-world quality or patient-safety decisions.

## Features

### AI-Powered Complaint Intake
- Analyze complaint descriptions using an AI workflow.
- Extract structured complaint information from unstructured text.
- Assess complaint completeness and identify missing information.
- Generate preliminary risk and priority assessments.

### Duplicate Complaint Detection
- Compare incoming complaints with existing records.
- Evaluate product, batch, complaint type, customer, and description similarity.
- Display potential matches with scores and explanations.
- Allow users to review duplicate warnings before proceeding.

### Complaint Management
- Create and manage pharmaceutical complaint records.
- Retrieve complaint details through the backend API.
- Persist complaint information in a SQL database.
- View complaint records through the frontend.

### Investigation and Quality Support
- Support investigation-related workflows.
- Generate preliminary root-cause recommendations.
- Provide corrective and preventive action (CAPA) recommendation support.
- Display dashboard summaries and recent complaint activity.

### User Interface
- React and TypeScript frontend.
- Redux Toolkit for application state management.
- API integration using Axios.
- Google Inter typography.
- Responsive application layout.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| State management | Redux Toolkit |
| API client | Axios |
| Backend | Python, FastAPI |
| AI workflow | LangGraph |
| Language model | Groq API, configured model such as `gemma2-9b-it` |
| Data validation | Pydantic |
| Database access | SQLAlchemy |
| Database | PostgreSQL |
| Testing | Pytest |
| Development tools | Git, GitHub, npm |

The configured model and database connection depend on your local environment settings.

## Architecture

```text
┌──────────────────────────────────┐
│       React + TypeScript         │
│    Complaint Management UI       │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       Redux Toolkit + Axios      │
│        Frontend State/API        │
└────────────────┬─────────────────┘
                 │ HTTP / REST
                 ▼
┌──────────────────────────────────┐
│           FastAPI                │
│  Complaint, AI, Dashboard APIs    │
└─────────┬────────────────┬───────┘
          │                │
          ▼                ▼
┌──────────────────┐  ┌──────────────────┐
│ LangGraph AI     │  │ SQLAlchemy       │
│ Analysis Workflow│  │ Database Access  │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Groq Language    │  │ PostgreSQL       │
│ Model API        │  │ Complaint Data   │
└──────────────────┘  └──────────────────┘
```

## Project Structure

```text
aivoa-ai-complaint-management/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── nodes/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   │   └── test_ai_rules.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
├── sample_data/
│   └── sample_complaint.txt
├── .gitignore
└── README.md
```

*The tree highlights the main application areas. Exact files may evolve as development continues.*

## Prerequisites

Install the following before running the project:

- Python 3.11 or a compatible Python version supported by the dependencies.
- Node.js and npm.
- PostgreSQL.
- A Groq API key for AI functionality.
- Git.

The project has been tested in a Windows PowerShell development environment using Python 3.13.5 and Vite 8.3.0.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/iravi0009/aivoa-ai-complaint-management.git
cd aivoa-ai-complaint-management
```

To use the latest feature branch instead of the default branch:

```bash
git checkout feature/qms-production-upgrade
```

### 2. Configure the backend

Open PowerShell from the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a local `backend/.env` file based on the configuration required by your backend. Configure the actual database URL and Groq API key expected by your application.

Example configuration keys (use the exact names expected by your code):

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/aivoa_db
GROQ_API_KEY=your_groq_api_key
```

Replace the example database credentials with your own local PostgreSQL credentials. Do not commit `.env` files or API keys to GitHub.

Create the database and run any database initialization or migration steps required by the application before starting the backend.

### 3. Start the backend

From the `backend` directory, with the virtual environment activated:

```powershell
python -m uvicorn app.main:app --reload
```

The backend should be available at:

- API base URL: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

The API documentation provides an interactive way to inspect and test available endpoints.

### 4. Configure and start the frontend

Open a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually:

http://localhost:5173/

Ensure that the frontend API base URL matches your running backend and that the backend CORS configuration allows the frontend origin.

### 5. Environment configuration

Keep configuration local and private.

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | Database connection string |
| `GROQ_API_KEY` | Authentication for the Groq API |
| Frontend API base URL | Address of the FastAPI backend |

These are example setting names. Confirm the actual names and required values against the current application configuration before running the project.

## API Overview

The backend exposes REST endpoints for complaint handling, AI analysis, duplicate detection, dashboards, and investigation-related workflows.

| Endpoint | Purpose |
|---|---|
| `POST /api/ai/analyze` | Analyze complaint text |
| `POST /api/ai/upload` | Upload and analyze complaint text |
| `POST /api/complaints` | Create a complaint |
| `POST /api/complaints/from-ai` | Create a complaint from AI-assisted intake |
| `POST /api/complaints/check-duplicate` | Check for potential duplicate complaints |
| `GET /api/complaints` | Retrieve complaint records |
| `GET /api/dashboard/summary` | Retrieve dashboard summary information |
| `GET /api/dashboard/recent` | Retrieve recent complaint activity |

Additional complaint detail, investigation, root-cause, and CAPA endpoints may be available in the current backend.

For exact request formats, response schemas, and all registered routes, open [FastAPI Swagger documentation](http://127.0.0.1:8000/docs) after starting the backend.

## Running Tests

### Backend tests

Activate the backend virtual environment and run:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ai_rules.py -v
```

The current AI rule test suite covers duplicate scoring, duplicate classifications, risk indicators, negated safety statements, and priority assignment.

### Python compilation check

```powershell
python -m compileall -q app
```

Run this command from the `backend` directory.

### Frontend production build

```powershell
cd frontend
npm install
npm run build
```

A successful Vite build confirms that the frontend can be compiled for production. It does not, by itself, prove that every user workflow works correctly.

## Demo Workflow

A typical demonstration can follow this sequence:

1. Open the complaint management dashboard.
2. Enter a fictional pharmaceutical complaint.
3. Run AI analysis and inspect extracted fields.
4. Review completeness, risk, and priority assessments.
5. Run duplicate detection and inspect any matches.
6. Save a complaint and verify it remains available after refreshing.
7. Demonstrate investigation and root-cause recommendation support.
8. Review the suggested CAPA and explain that QA review is required.
9. Open the FastAPI documentation and show the automated test results.

Use fictional data for public demonstrations.

## Security and Data Handling

- Never commit API keys, database passwords, access tokens, or private `.env` files.
- Use fictional or appropriately anonymized data in demonstrations.
- Apply appropriate authentication and authorization before exposing the application to external users.
- Protect complaint and customer information from unauthorized access.
- Validate uploaded files and incoming API data.
- Review AI-generated outputs before using them in operational decisions.

## Limitations

This project is an AI-assisted prototype, not a validated pharmaceutical quality management system.

- AI outputs may be incomplete, incorrect, or inconsistent.
- Risk and priority assessments are preliminary and rule/model dependent.
- Duplicate detection can produce false positives or miss similar complaints.
- Root-cause and CAPA suggestions are recommendations, not verified conclusions.
- Regulatory compliance, audit trails, electronic signatures, access controls, validation, and production deployment requirements must be independently assessed before regulated use.

Qualified quality personnel remain responsible for final decisions.

## Future Improvements

Potential areas for future development include:

- Role-based authentication and authorization.
- Comprehensive audit trails and change history.
- More robust database migrations and deployment configuration.
- Expanded automated integration and end-to-end tests.
- Improved duplicate matching and explainability.
- Human review and approval workflows.
- Monitoring, logging, and production observability.
- Formal validation and regulatory assessment for any intended regulated use.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and add appropriate tests.
4. Run the relevant backend tests and frontend build.
5. Open a pull request with a clear description of the changes.

## License

No license has been specified in this repository documentation yet. Unless a license is added to the repository, reuse and redistribution are subject to the applicable copyright terms.

---

**AIVOA.AI — AI-assisted pharmaceutical complaint management, with human oversight at every critical decision.**
