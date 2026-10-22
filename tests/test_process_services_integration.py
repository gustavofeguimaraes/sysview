from app.services.process_services import (
    get_process_service_summary,
)


def test_process_service_summary_invalid_pid():
    result = get_process_service_summary(
        999999999
    )

    assert result is None


def test_process_service_summary_structure():
    import os

    pid = os.getpid()

    result = get_process_service_summary(
        pid
    )

    assert result is not None

    assert "pid" in result
    assert "process" in result
    assert "username" in result
    assert "exe" in result

    assert "total_services" in result
    assert "running" in result
    assert "stopped" in result
    assert "other" in result
    assert "services" in result


def test_process_service_summary_counts_are_valid():
    import os

    pid = os.getpid()

    result = get_process_service_summary(
        pid
    )

    assert result is not None

    assert result["total_services"] >= 0
    assert result["running"] >= 0
    assert result["stopped"] >= 0
    assert result["other"] >= 0

    assert isinstance(
        result["services"],
        list,
    )