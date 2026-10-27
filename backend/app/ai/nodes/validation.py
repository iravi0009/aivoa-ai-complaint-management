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

    is_complete = not missing_fields

    warnings = []

    if missing_fields:
        warnings.append(
            "Complaint requires review because required information is missing."
        )

    completeness = {
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "warnings": warnings,
    }

    return {
        **state,
        "completeness": completeness,
    }