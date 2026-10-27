
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.ai.graph import complaint_graph
from app.core.config import settings
from app.services.document_service import extract_text
from app.schemas.complaint import AIAnalysisResponse


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class AnalyzeRequest(BaseModel):
    text: str


def run_analysis(text: str) -> dict:
    """Run LangGraph and validate its structured analysis."""

    result = complaint_graph.invoke(
        {
            "input_text": text,
            "errors": [],
        }
    )

    analysis = AIAnalysisResponse.model_validate(
        {
            "complaint": result.get("complaint"),
            "completeness": result.get("completeness"),
            "risk_assessment": result.get("risk_assessment"),
            "priority_assessment": result.get("priority_assessment"),
        }
    )

    return {
        "success": True,
        "result": {
            **analysis.model_dump(mode="json"),
            "errors": result.get("errors", []),
        },
    }


@router.post("/analyze")
def analyze_complaint(request: AnalyzeRequest):
    """Analyze complaint text using LangGraph and Groq."""

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Complaint text cannot be empty.",
        )

    try:
        return run_analysis(request.text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {exc}",
        ) from exc


@router.post("/upload")
async def upload_complaint(file: UploadFile = File(...)):
    """Extract text from a complaint document and analyze it."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = file.filename
    extension = "." + filename.rsplit(".", 1)[-1].lower()

    allowed_extensions = {".pdf", ".docx", ".txt", ".eml"}

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Supported formats: PDF, DOCX, TXT, EML.",
        )

    max_size = settings.max_upload_size_mb * 1024 * 1024
    file_bytes = await file.read()

    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large. Maximum size is "
                f"{settings.max_upload_size_mb} MB."
            ),
        )

    try:
        extracted_text = extract_text(filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document extraction failed: {exc}",
        ) from exc

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable complaint text was found.",
        )

    try:
        analysis = run_analysis(extracted_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI complaint analysis failed: {exc}",
        ) from exc

    return {
        **analysis,
        "filename": filename,
        "file_type": extension,
        "extracted_text": extracted_text,
    }
