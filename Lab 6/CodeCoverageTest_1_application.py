import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def test_general_order():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "orders": [{"qty": 2, "promo": ""}]
    }]
    result = process_ticket_manifest(manifests, 0.1)
    assert result == {"total_revenue": 99.0, "status": "COMPLETED"}


def test_vip_order_with_lounge():
    manifests = [{
        "is_confirmed": True,
        "tier": "vip",
        "exclusive_lounge": True,
        "orders": [{"qty": 2, "promo": ""}]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result == {"total_revenue": 375.0, "status": "COMPLETED"}


def test_premium_earlybird():
    manifests = [{
        "is_confirmed": True,
        "tier": "premium",
        "orders": [{"qty": 2, "promo": "EARLYBIRD"}]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 144.0


def test_general_bulk_discount():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "orders": [{"qty": 5, "promo": ""}]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 205.0


def test_unconfirmed_manifest():
    result = process_ticket_manifest(
        [{"is_confirmed": False, "tier": "vip",
          "orders": [{"qty": 2}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_unknown_tier_rejected():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "student",
          "orders": [{"qty": 2}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_invalid_quantity():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 0}, {"qty": -1}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_fraud_risk_non_vip():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 2, "promo": "FRAUD_RISK"}]}], 0
    )
    assert result == {"total_revenue": 90.0, "status": "COMPLETED"}


def test_vip_fraud_resets_manifest_total():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "vip",
          "orders": [{"qty": 2, "promo": "FRAUD_RISK"}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_audit_rejected():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "orders": [
            {"qty": 0}, {"qty": 0}, {"qty": 0},
            {"qty": 0}, {"qty": 0}
        ]
    }, {
        "is_confirmed": True,
        "tier": "vip",
        "orders": [{"qty": 1}]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result["status"] == "AUDIT_REJECTED"
    assert result["total_revenue"] == 150.0


def test_empty_manifest_list():
    result = process_ticket_manifest([], 0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_invalid_manifest_type():
    with pytest.raises(ValueError):
        process_ticket_manifest("not a list", 0)


def test_negative_tax_rate():
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.1)


def test_gate_flow_no_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_gate_flow_normal():
    assert monitor_gate_flow([[10, 30, 50, 20]]) == "FLOW_NORMAL"


def test_gate_flow_overflow():
    assert monitor_gate_flow([[60, 70]]) == "OVERFLOW"


def test_gate_flow_streak_reset():
    assert monitor_gate_flow([[60, 40, 60, 70]]) == "OVERFLOW"


def test_gate_flow_separate_streams():
    assert monitor_gate_flow([[60], [70, 80]]) == "OVERFLOW"


def test_gate_flow_empty_stream():
    assert monitor_gate_flow([[]]) == "FLOW_NORMAL"