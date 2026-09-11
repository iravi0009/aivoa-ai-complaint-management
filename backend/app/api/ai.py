from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.ai.graph import complaint_graph
from app.core.config import settings
from app.services.document_service import extract_text


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class AnalyzeRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze_complaint(request: AnalyzeRequest):
    """
    Analyze complaint text using LangGraph + Groq.
    """

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Complaint text cannot be empty.",
        )

    result = complaint_graph.invoke(
        {
            "input_text": request.text,
            "errors": [],
        }
    )

    return {
        "success": True,
        "result": result,
    }


@router.post("/upload")
async def upload_complaint(
    file: UploadFile = File(...),
):
    """
    Upload PDF/DOCX/TXT/EML complaint document,
    extract its text, then run the existing
    LangGraph complaint analysis pipeline.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = file.filename

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".eml",
    }

    extension = "." + filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Supported formats: PDF, DOCX, TXT, EML."
            ),
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
        extracted_text = extract_text(
            filename,
            file_bytes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

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
        result = complaint_graph.invoke(
            {
                "input_text": extracted_text,
                "errors": [],
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI complaint analysis failed: {exc}",
        ) from exc

    return {
        "success": True,
        "filename": filename,
        "file_type": extension,
        "extracted_text": extracted_text,
        "result": result,
    }