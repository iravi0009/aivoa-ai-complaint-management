from app.ai.state import ComplaintState


REQUIRED_FIELDS = [
    "customer_name",
    "product_name",
    "batch_number",
    "complaint_type",
    "complaint_date",
    "description",
]


def validation_node(state: ComplaintState) -> ComplaintState:
    complaint = state.get("complaint", {})

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if not complaint.get(field)
    ]

    total_fields = len(REQUIRED_FIELDS)
    available_fields = total_fields - len(missing_fields)

    score = round(
        (available_fields / total_fields) * 100
    )

    completeness = {
        "score": score,
        "missing_fields": missing_fields,
        "status": (
            "Complete"
            if not missing_fields
            else "Needs Review"
        ),
    }

    return {
        **state,
        "completeness": completeness,
    }