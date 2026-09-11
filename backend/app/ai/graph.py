from langgraph.graph import END, START, StateGraph

from app.ai.state import ComplaintState
from app.ai.nodes.extraction import extraction_node
from app.ai.nodes.validation import validation_node
from app.ai.nodes.risk import risk_node
from app.ai.nodes.priority import priority_node
from app.ai.nodes.finalize import finalize_node


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

    graph.add_edge(
        "extract_complaint",
        "validate_complaint",
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