from app.ai.state import ComplaintState


HIGH_RISK_KEYWORDS = [
    "contamination",
    "adverse event",
    "serious reaction",
    "incorrect strength",
    "wrong product",
    "sterility",
    "foreign particle",
    "recall",
]


def risk_node(state: ComplaintState) -> ComplaintState:
    complaint = state.get("complaint", {})

    description = (
        complaint.get("description") or ""
    ).lower()

    complaint_type = (
        complaint.get("complaint_type") or ""
    ).lower()

    combined_text = (
        f"{description} {complaint_type}"
    )

    if any(
        keyword in combined_text
        for keyword in HIGH_RISK_KEYWORDS
    ):
        level = "Critical"
        severity = "Critical"
        confidence = 0.90

        reason = (
            "The complaint contains indicators that "
            "may represent a significant product or "
            "patient safety concern."
        )

    elif complaint_type == "product quality":
        level = "High"
        severity = "Major"
        confidence = 0.85

        reason = (
            "The complaint indicates a potential "
            "product quality issue requiring investigation."
        )

    elif complaint_type in {
        "packaging",
        "labeling",
    }:
        level = "Medium"
        severity = "Moderate"
        confidence = 0.82

        reason = (
            "The complaint may affect product presentation "
            "or information supplied to the customer."
        )

    else:
        level = "Low"
        severity = "Minor"
        confidence = 0.78

        reason = (
            "The available complaint information does not "
            "indicate a significant quality or safety concern."
        )

    return {
        **state,
        "risk_assessment": {
            "risk_level": level,
            "severity": severity,
            "confidence": confidence,
            "reason": reason,
        },
    }