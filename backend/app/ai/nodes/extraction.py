from app.ai.state import ComplaintState
from app.services.ai_service import extract_complaint


def extraction_node(state: ComplaintState) -> ComplaintState:
    try:
        complaint = extract_complaint(
            state["input_text"]
        )

        return {
            **state,
            "complaint": complaint,
        }

    except Exception as exc:
        return {
            **state,
            "errors": [
                *state.get("errors", []),
                f"Extraction error: {exc}",
            ],
        }