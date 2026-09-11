from app.ai.state import ComplaintState


def finalize_node(state: ComplaintState) -> ComplaintState:
    result = {
        "complaint": state.get(
            "complaint",
            {},
        ),
        "completeness": state.get(
            "completeness",
            {},
        ),
        "risk_assessment": state.get(
            "risk_assessment",
            {},
        ),
        "priority_assessment": state.get(
            "priority_assessment",
            {},
        ),
        "errors": state.get(
            "errors",
            [],
        ),
    }

    return {
        **state,
        "final_result": result,
    }