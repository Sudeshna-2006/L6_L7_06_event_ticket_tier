
import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def test_invalid_manifest_type():
    with pytest.raises(ValueError):
        process_ticket_manifest("invalid", 0.1)


def test_negative_tax():
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.1)


def test_unconfirmed_manifest():
    result = process_ticket_manifest(
        [{"is_confirmed": False, "tier": "vip",
          "orders": [{"qty": 1}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_vip_tier():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "vip",
          "orders": [{"qty": 1, "promo": ""}]}], 0
    )
    assert result["total_revenue"] == 150.0


def test_premium_tier():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "premium",
          "orders": [{"qty": 1, "promo": ""}]}], 0
    )
    assert result["total_revenue"] == 90.0


def test_general_tier():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 1, "promo": ""}]}], 0
    )
    assert result["total_revenue"] == 45.0


def test_unknown_tier():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "unknown",
          "orders": [{"qty": 1}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_zero_quantity():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 0}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_negative_quantity():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": -1}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_earlybird_promotion():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "premium",
          "orders": [{"qty": 2, "promo": "EARLYBIRD"}]}], 0
    )
    assert result["total_revenue"] == 144.0


def test_fraud_non_vip():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 1, "promo": "FRAUD_RISK"}]}], 0
    )
    assert result["total_revenue"] == 45.0


def test_fraud_vip():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "vip",
          "orders": [{"qty": 1, "promo": "FRAUD_RISK"}]}], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_bulk_discount():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 5, "promo": ""}]}], 0
    )
    assert result["total_revenue"] == 205.0


def test_lounge_charge():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "exclusive_lounge": True, "orders": []}], 0
    )
    assert result["total_revenue"] == 75.0


def test_zero_sales():
    result = process_ticket_manifest([], 0)
    assert result["status"] == "ZERO_SALES"


def test_audit_rejection():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "orders": [{"qty": 0} for _ in range(5)]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result["status"] == "AUDIT_REJECTED"


def test_completed_status():
    result = process_ticket_manifest(
        [{"is_confirmed": True, "tier": "general",
          "orders": [{"qty": 1}]}], 0.1
    )
    assert result["status"] == "COMPLETED"


def test_gate_no_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_gate_normal_flow():
    assert monitor_gate_flow([[10, 20, 50]]) == "FLOW_NORMAL"


def test_gate_overflow():
    assert monitor_gate_flow([[60, 70]]) == "OVERFLOW"


def test_gate_streak_reset():
    assert monitor_gate_flow([[60, 40, 60, 70]]) == "OVERFLOW"


def test_gate_multiple_streams():
    assert monitor_gate_flow([[60], [70, 80]]) == "OVERFLOW"


def test_gate_empty_stream():
    assert monitor_gate_flow([[]]) == "FLOW_NORMAL"
