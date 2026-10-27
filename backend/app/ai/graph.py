from langgraph.graph import END, START, StateGraph

from app.ai.state import ComplaintState
from app.ai.nodes.extraction import extraction_node
from app.ai.nodes.validation import validation_node
from app.ai.nodes.risk import risk_node
from app.ai.nodes.priority import priority_node
from app.ai.nodes.finalize import finalize_node


def extraction_route(state: ComplaintState) -> str:
    """
    Route the graph based on extraction success.

    Extraction must contain meaningful complaint information
    before validation, risk, and priority assessment can run.
    """

    # AI/model or extraction error
    if state.get("errors"):
        return "error"

    complaint = state.get("complaint")

    # No extracted complaint
    if not complaint:
        return "error"

    # Core fields used to determine whether the extraction
    # contains meaningful complaint information.
    meaningful_fields = [
        "customer_name",
        "product_name",
        "batch_number",
        "complaint_type",
        "complaint_date",
        "description",
    ]

    # At least one meaningful field must contain information.
    has_meaningful_data = any(
        complaint.get(field) not in (None, "")
        for field in meaningful_fields
    )

    if not has_meaningful_data:
        return "error"

    return "success"


def build_complaint_graph():
    graph = StateGraph(ComplaintState)

    graph.add_node(
        "extract_complaint",
        extraction_node,
    )

    graph.add_node(
        "validate_complaint",
        validation_node,
    )

    graph.add_node(
        "assess_risk",
        risk_node,
    )

    graph.add_node(
        "assess_priority",
        priority_node,
    )

    graph.add_node(
        "finalize",
        finalize_node,
    )

    graph.add_edge(
        START,
        "extract_complaint",
    )

    graph.add_conditional_edges(
        "extract_complaint",
        extraction_route,
        {
            "success": "validate_complaint",
            "error": "finalize",
        },
    )

    graph.add_edge(
        "validate_complaint",
        "assess_risk",
    )

    graph.add_edge(
        "assess_risk",
        "assess_priority",
    )

    graph.add_edge(
        "assess_priority",
        "finalize",
    )

    graph.add_edge(
        "finalize",
        END,
    )

    return graph.compile()


complaint_graph = build_complaint_graph()