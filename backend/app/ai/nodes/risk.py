from app.ai.state import ComplaintState


SAFETY_KEYWORDS = [
    "adverse event",
    "serious reaction",
    "patient injury",
    "hospitalization",
    "death",
    "allergic reaction",
    "overdose",
]

CRITICAL_QUALITY_KEYWORDS = [
    "contamination",
    "contaminated",
    "sterility issue",
    "sterility problem",
    "wrong product",
    "incorrect strength",
    "wrong strength",
    "strength mismatch",
    "incorrect dosage",
    "wrong dosage",
    "wrong dose",
    "incorrect dose",
    "wrong potency",
    "foreign particle",
    "foreign particles",
    "recall",
]

QUALITY_KEYWORDS = [
    "discoloration",
    "brownish",
    "black",
    "odor",
    "smell",
    "tablet defect",
    "dissolution",
    "impurity",
]

NEGATION_PHRASES = [
    "no ",
    "no reported",
    "not reported",
    "without ",
    "denies ",
    "denied ",
    "none reported",
    "was not ",
    "were not ",
    "did not ",
    "does not ",
]

RISK_THRESHOLDS = {
    "CRITICAL": 70,
    "HIGH": 45,
    "MEDIUM": 20,
}

RISK_WEIGHTS = {
    "patient_safety": 50,
    "critical_quality": 40,
    "product_quality": 20,
    "adverse_event_type": 35,
    "product_quality_type": 15,
    "packaging_labeling_type": 10,
    "batch_available": 5,
    "incomplete_complaint": 5,
}


def _contains_keyword(
    text: str,
    keywords: list[str],
) -> list[str]:
    """Return matching indicators that are not immediately negated."""

    matches = []

    for keyword in keywords:
        start = 0

        while True:
            index = text.find(keyword, start)

            if index == -1:
                break

            context_start = max(0, index - 30)
            context = text[context_start:index]

            if not any(
                phrase in context
                for phrase in NEGATION_PHRASES
            ):
                matches.append(keyword)
                break

            start = index + len(keyword)

    return matches


def risk_node(state: ComplaintState) -> ComplaintState:
    """
    Calculate an explainable complaint risk assessment.

    Risk is based on multiple factors rather than a single
    keyword or complaint type.
    """

    complaint = state.get("complaint", {})
    completeness = state.get("completeness", {})

    description = (
        complaint.get("description") or ""
    ).lower()

    complaint_type = (
        complaint.get("complaint_type") or ""
    ).strip().lower()

    combined_text = f"{description} {complaint_type}"

    score = 0
    factors: list[str] = []

    # --------------------------------------------------------
    # 1. Patient safety indicators
    # --------------------------------------------------------

    safety_matches = _contains_keyword(
        combined_text,
        SAFETY_KEYWORDS,
    )

    if safety_matches:
        score += RISK_WEIGHTS["patient_safety"]

        factors.append(
            "Patient safety indicator: "
            + ", ".join(safety_matches)
        )

    # --------------------------------------------------------
    # 2. Critical product quality indicators
    # --------------------------------------------------------

    critical_quality_matches = _contains_keyword(
        combined_text,
        CRITICAL_QUALITY_KEYWORDS,
    )

    if critical_quality_matches:
        score += RISK_WEIGHTS["critical_quality"]

        factors.append(
            "Critical quality indicator: "
            + ", ".join(critical_quality_matches)
        )

    # --------------------------------------------------------
    # 3. General product quality indicators
    # --------------------------------------------------------

    quality_matches = _contains_keyword(
        combined_text,
        QUALITY_KEYWORDS,
    )

    if quality_matches:
        score += RISK_WEIGHTS["product_quality"]

        factors.append(
            "Product quality indicator: "
            + ", ".join(quality_matches)
        )

    # --------------------------------------------------------
    # 4. Complaint type
    # --------------------------------------------------------

    if complaint_type == "adverse event":
        score += RISK_WEIGHTS["adverse_event_type"]

        factors.append(
            "Complaint type indicates a potential "
            "patient safety concern."
        )

    elif complaint_type == "product quality":
        score += RISK_WEIGHTS["product_quality_type"]

        factors.append(
            "Complaint is classified as Product Quality."
        )

    elif complaint_type in {
        "packaging",
        "labeling",
    }:
        score += RISK_WEIGHTS["packaging_labeling_type"]

        factors.append(
            "Complaint involves packaging or labeling."
        )

    # --------------------------------------------------------
    # 5. Batch information
    # --------------------------------------------------------

    if complaint.get("batch_number"):
        score += RISK_WEIGHTS["batch_available"]

        factors.append(
            "Affected batch/lot information is available."
        )
    else:
        factors.append(
            "Batch/lot information is missing."
        )

    # --------------------------------------------------------
    # 6. Complaint completeness
    # --------------------------------------------------------

    is_complete = completeness.get("is_complete")

    if is_complete is False:
        factors.append(
            "Complaint information is incomplete."
        )

    elif is_complete is True:
        factors.append(
            "Complaint contains sufficient information for triage."
        )


    # --------------------------------------------------------
    # 7. Convert score to risk level
    # --------------------------------------------------------

    # Critical quality indicators require immediate QA review.
    # Negated indicators are already filtered by _contains_keyword.
    if (
        safety_matches
        or critical_quality_matches
        or score >= RISK_THRESHOLDS["CRITICAL"]
    ):
        level = "Critical"
        severity = "Critical"

    elif score >= RISK_THRESHOLDS["HIGH"]:
        level = "High"
        severity = "Major"

    elif score >= RISK_THRESHOLDS["MEDIUM"]:
        level = "Medium"
        severity = "Moderate"

    else:
        level = "Low"
        severity = "Minor"

    # --------------------------------------------------------
    # 8. Explainable confidence
    # --------------------------------------------------------

    if safety_matches or critical_quality_matches:
        confidence = 0.95

    elif quality_matches or complaint_type == "product quality":
        confidence = 0.88

    elif complaint_type in {
        "packaging",
        "labeling",
    }:
        confidence = 0.82

    else:
        confidence = 0.75

    # Reduce confidence when the complaint is incomplete.
    if is_complete is False:
        confidence = max(
            0.60,
            confidence - 0.10,
        )

    # --------------------------------------------------------
    # 9. Explainable reasoning
    # --------------------------------------------------------

    reasoning = (
        f"Risk score: {score}. "
        f"Classification: {level}. "
        f"Contributing factors: "
        f"{'; '.join(factors)}"
    )

    return {
        **state,
        "risk_assessment": {
            "risk_level": level.upper(),
            "severity": severity.upper(),
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "score": score,
            "factors": factors,
        },
    }