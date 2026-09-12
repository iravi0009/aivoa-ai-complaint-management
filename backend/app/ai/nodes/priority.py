from app.ai.state import ComplaintState


def priority_node(state: ComplaintState) -> ComplaintState:
    """
    Calculate complaint priority using risk, patient-safety signals,
    batch information, and complaint completeness.

    Priority:
        P1 = Immediate / urgent QA attention
        P2 = High attention
        P3 = Routine attention
    """

    risk = state.get("risk_assessment", {})
    complaint = state.get("complaint", {})
    completeness = state.get("completeness", {})

    risk_level = str(risk.get("risk_level", "LOW")).upper()
    risk_score = int(risk.get("score", 0) or 0)

    description = str(complaint.get("description") or "").lower()
    complaint_type = str(
        complaint.get("complaint_type") or ""
    ).lower()

    factors = []
    priority_score = risk_score

    # ---------------------------------------------------------
    # 1. Risk level
    # ---------------------------------------------------------
    if risk_level == "CRITICAL":
        priority_score += 30
        factors.append("Critical risk classification.")

    elif risk_level == "HIGH":
        priority_score += 15
        factors.append("High risk classification.")

    elif risk_level == "MEDIUM":
        factors.append("Medium risk classification.")

    else:
        factors.append("Low risk classification.")

    # ---------------------------------------------------------
    # 2. Patient safety signals
    # ---------------------------------------------------------
    patient_safety_keywords = [
        "adverse event",
        "serious reaction",
        "patient injury",
        "hospitalization",
        "death",
        "allergic reaction",
        "overdose",
    ]

    matched_safety = [
        keyword
        for keyword in patient_safety_keywords
        if keyword in description
    ]

    if matched_safety:
        priority_score += 25
        factors.append(
            f"Patient safety signal: {', '.join(matched_safety)}."
        )

    # Complaint classification can also indicate patient impact.
    if complaint_type in {
        "adverse event",
        "serious adverse event",
        "patient safety",
    }:
        priority_score += 25
        factors.append(
            "Complaint type indicates potential patient safety impact."
        )

    # ---------------------------------------------------------
    # 3. Batch information
    # ---------------------------------------------------------
    batch_number = complaint.get("batch_number")

    if batch_number:
        factors.append("Affected batch/lot is identified.")
    else:
        factors.append("Batch/lot information is unavailable.")

    # ---------------------------------------------------------
    # 4. Completeness
    # ---------------------------------------------------------
    completeness_score = completeness.get("score")

    if completeness_score is not None:
        try:
            completeness_score = float(completeness_score)

            if completeness_score < 60:
                factors.append(
                    "Complaint information is substantially incomplete."
                )
            elif completeness_score < 80:
                factors.append(
                    "Some complaint information is missing."
                )
            else:
                factors.append(
                    "Complaint contains sufficient information for triage."
                )

        except (TypeError, ValueError):
            pass

    # ---------------------------------------------------------
    # 5. Final priority
    # ---------------------------------------------------------
    if risk_level == "CRITICAL" or priority_score >= 90:
        priority = "P1"

    elif risk_level == "HIGH" or priority_score >= 45:
        priority = "P1"

    elif risk_level == "MEDIUM" or priority_score >= 20:
        priority = "P2"

    else:
        priority = "P3"

    return {
        **state,
        "priority_assessment": {
            "priority": priority,
            "score": priority_score,
            "factors": factors,
        },
    }
