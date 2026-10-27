from difflib import SequenceMatcher
from typing import Any


def normalize(value: Any) -> str:
    if value is None:
        return ""

    return " ".join(str(value).lower().strip().split())


def similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0

    return SequenceMatcher(
        None,
        normalize(text1),
        normalize(text2),
    ).ratio()


def calculate_duplicate_score(
    new_complaint: dict,
    existing_complaint: dict,
) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    new_product = normalize(new_complaint.get("product_name"))
    old_product = normalize(existing_complaint.get("product_name"))

    if new_product and old_product and new_product == old_product:
        score += 25
        reasons.append("Same product")

    new_batch = normalize(new_complaint.get("batch_number"))
    old_batch = normalize(existing_complaint.get("batch_number"))

    if new_batch and old_batch and new_batch == old_batch:
        score += 30
        reasons.append("Same batch/lot")

    new_type = normalize(new_complaint.get("complaint_type"))
    old_type = normalize(existing_complaint.get("complaint_type"))

    if new_type and old_type and new_type == old_type:
        score += 15
        reasons.append("Same complaint type")

    new_customer = normalize(new_complaint.get("customer_name"))
    old_customer = normalize(existing_complaint.get("customer_name"))

    if new_customer and old_customer and new_customer == old_customer:
        score += 10
        reasons.append("Same customer")

    description_similarity = similarity(
        new_complaint.get("description"),
        existing_complaint.get("description"),
    )

    if description_similarity >= 0.80:
        score += 20
        reasons.append("Very similar complaint description")
    elif description_similarity >= 0.60:
        score += 10
        reasons.append("Similar complaint description")

    return score, reasons


def detect_duplicate(
    new_complaint: dict,
    existing_complaints: list[dict],
) -> dict:
    matches = []

    for complaint in existing_complaints:
        score, reasons = calculate_duplicate_score(
            new_complaint,
            complaint,
        )

        if score >= 50:
            matches.append(
                {
                    "complaint_id": complaint.get("id"),
                    "complaint_number": complaint.get(
                        "complaint_number"
                    ),
                    "score": score,
                    "reasons": reasons,
                }
            )

    matches.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if not matches:
        duplicate_status = "NO_DUPLICATE"
    elif matches[0]["score"] >= 80:
        duplicate_status = "HIGH_CONFIDENCE_DUPLICATE"
    else:
        duplicate_status = "POTENTIAL_DUPLICATE"

    return {
        "is_duplicate": len(matches) > 0,
        "duplicate_status": duplicate_status,
        "matches": matches[:5],
    }