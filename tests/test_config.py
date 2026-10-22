import pytest

from app.core.config import (
    MONITOR_INTERVALS,
    REQUIRED_MONITOR_INTERVALS,
    validate_monitor_intervals,
)


def test_monitor_intervals_are_dictionary():
    assert isinstance(
        MONITOR_INTERVALS,
        dict,
    )


def test_monitor_intervals_contain_all_required_keys():
    assert REQUIRED_MONITOR_INTERVALS <= set(
        MONITOR_INTERVALS.keys()
    )


def test_monitor_intervals_are_positive_numbers():
    for value in MONITOR_INTERVALS.values():
        assert isinstance(
            value,
            (int, float),
        )
        assert value > 0


def test_validate_monitor_intervals_returns_copy():
    result = validate_monitor_intervals(
        MONITOR_INTERVALS
    )

    assert isinstance(result, dict)
    assert result == MONITOR_INTERVALS
    assert result is not MONITOR_INTERVALS


def test_validate_monitor_intervals_accepts_valid_values():
    intervals = {
        "dashboard": 1,
        "network": 2,
        "network_connections": 3,
        "process": 4,
        "process_network": 5,
        "process_services": 6,
        "services": 7,
        "system": 8,
    }

    result = validate_monitor_intervals(
        intervals
    )

    assert result["dashboard"] == 1.0
    assert result["system"] == 8.0


def test_validate_monitor_intervals_rejects_missing_key():
    intervals = dict(MONITOR_INTERVALS)

    intervals.pop("network")

    with pytest.raises(ValueError):
        validate_monitor_intervals(
            intervals
        )


def test_validate_monitor_intervals_rejects_zero():
    intervals = dict(MONITOR_INTERVALS)

    intervals["network"] = 0

    with pytest.raises(ValueError):
        validate_monitor_intervals(
            intervals
        )


def test_validate_monitor_intervals_rejects_negative():
    intervals = dict(MONITOR_INTERVALS)

    intervals["process"] = -1

    with pytest.raises(ValueError):
        validate_monitor_intervals(
            intervals
        )


def test_validate_monitor_intervals_rejects_text():
    intervals = dict(MONITOR_INTERVALS)

    intervals["services"] = "10"

    with pytest.raises(TypeError):
        validate_monitor_intervals(
            intervals
        )


def test_validate_monitor_intervals_rejects_boolean():
    intervals = dict(MONITOR_INTERVALS)

    intervals["system"] = True

    with pytest.raises(TypeError):
        validate_monitor_intervals(
            intervals
        )


def test_validate_monitor_intervals_rejects_non_dictionary():
    with pytest.raises(TypeError):
        validate_monitor_intervals(
            ["invalid"]
        )