from app.ai.state import ComplaintState


def priority_node(state: ComplaintState) -> ComplaintState:
    risk = state.get("risk_assessment", {})

    risk_level = risk.get(
        "risk_level",
        "Low",
    )

    priority_map = {
        "Critical": "Critical",
        "High": "High",
        "Medium": "Medium",
        "Low": "Low",
    }

    priority = priority_map.get(
        risk_level,
        "Medium",
    )

    return {
        **state,
        "priority_assessment": {
            "priority": priority,
        },
    }