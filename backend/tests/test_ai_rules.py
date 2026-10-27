from app.services.duplicate_detector import (
    calculate_duplicate_score,
    detect_duplicate,
)
from app.ai.nodes.risk import risk_node
from app.ai.nodes.priority import priority_node


def test_duplicate_score_detects_same_batch_and_product():
    new = {
        "product_name": "Paracetamol Tablets",
        "batch_number": "PCM-240821",
        "complaint_type": "Product Quality",
        "customer_name": "ABC Pharmaceuticals",
        "description": "Brown discoloration on tablets",
    }
    existing = {
        "id": 1,
        "complaint_number": "CMP-00001",
        "product_name": "paracetamol tablets",
        "batch_number": "PCM-240821",
        "complaint_type": "Product Quality",
        "customer_name": "ABC Pharmaceuticals",
        "description": "Brown discoloration on tablets",
    }

    score, reasons = calculate_duplicate_score(new, existing)

    assert score == 100
    assert "Same product" in reasons
    assert "Same batch/lot" in reasons


def test_duplicate_detector_returns_potential_duplicate():
    new = {
        "product_name": "Paracetamol",
        "batch_number": "BATCH-1",
        "complaint_type": "Product Quality",
    }
    existing = {
        "id": 7,
        "complaint_number": "CMP-00007",
        "product_name": "Paracetamol",
        "batch_number": "BATCH-1",
        "complaint_type": "Other",
    }

    result = detect_duplicate(new, [existing])

    assert result["is_duplicate"] is True
    assert result["duplicate_status"] == "POTENTIAL_DUPLICATE"
    assert result["matches"][0]["complaint_id"] == 7


def test_duplicate_detector_returns_no_duplicate():
    new = {
        "product_name": "Paracetamol",
        "batch_number": "BATCH-1",
        "description": "Brown discoloration",
    }
    existing = {
        "id": 2,
        "product_name": "Ibuprofen",
        "batch_number": "BATCH-9",
        "description": "Broken packaging",
    }

    result = detect_duplicate(new, [existing])

    assert result["is_duplicate"] is False
    assert result["duplicate_status"] == "NO_DUPLICATE"
    assert result["matches"] == []


def test_risk_node_recognizes_critical_quality_signal():
    state = {
        "complaint": {
            "description": "Foreign particles observed in tablets",
            "complaint_type": "Product Quality",
            "batch_number": "BATCH-1",
        },
        "completeness": {"is_complete": True},
    }

    result = risk_node(state)
    assessment = result["risk_assessment"]

    assert assessment["risk_level"] == "CRITICAL"
    assert assessment["score"] == 60
    assert any(
        "Critical quality indicator" in factor
        for factor in assessment["factors"]
    )


def test_risk_node_does_not_count_negated_patient_injury():
    state = {
        "complaint": {
            "description": (
                "Discoloration observed. "
                "No patient injury was reported."
            ),
            "complaint_type": "Product Quality",
            "batch_number": "BATCH-1",
        },
        "completeness": {"is_complete": False},
    }

    result = risk_node(state)
    assessment = result["risk_assessment"]

    assert not any(
        "Patient safety indicator" in factor
        for factor in assessment["factors"]
    )
    assert assessment["risk_level"] == "MEDIUM"


def test_risk_node_does_not_count_negated_contamination():
    state = {
        "complaint": {
            "description": "No contamination was observed.",
            "complaint_type": "Other",
            "batch_number": "BATCH-1",
        },
        "completeness": {"is_complete": True},
    }

    result = risk_node(state)
    assessment = result["risk_assessment"]

    assert not any(
        "Critical quality indicator" in factor
        for factor in assessment["factors"]
    )
    assert assessment["risk_level"] == "LOW"


def test_priority_node_returns_p2_for_medium_risk():
    state = {
        "complaint": {
            "description": "Brown discoloration observed",
            "complaint_type": "Product Quality",
            "batch_number": "BATCH-1",
        },
        "completeness": {"is_complete": False},
        "risk_assessment": {
            "risk_level": "MEDIUM",
            "score": 40,
        },
    }

    result = priority_node(state)

    assert result["priority_assessment"]["priority"] == "P2"


def test_priority_node_does_not_promote_negated_injury():
    state = {
        "complaint": {
            "description": "No patient injury was reported.",
            "complaint_type": "Other",
            "batch_number": "BATCH-1",
        },
        "completeness": {"is_complete": True},
        "risk_assessment": {
            "risk_level": "LOW",
            "score": 5,
        },
    }

    result = priority_node(state)

    assert result["priority_assessment"]["priority"] == "P3"
