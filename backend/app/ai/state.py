from typing import Any, TypedDict


class ComplaintState(TypedDict, total=False):
    input_text: str

    complaint: dict[str, Any]
    completeness: dict[str, Any]

    risk_assessment: dict[str, Any]
    priority_assessment: dict[str, Any]

    final_result: dict[str, Any]

    errors: list[str]