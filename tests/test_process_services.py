import psutil

from app.services.process_services import (
    get_processes_with_services,
)


def test_get_processes_with_services_returns_list():
    result = get_processes_with_services()

    assert isinstance(result, list)


def test_processes_with_services_have_expected_structure():
    result = get_processes_with_services()

    if not result:
        return

    process = result[0]

    assert "pid" in process
    assert "process" in process
    assert "username" in process
    assert "exe" in process
    assert "services" in process
    assert "running" in process
    assert "stopped" in process
    assert "service_list" in process


def test_processes_with_services_have_valid_pid():
    result = get_processes_with_services()

    for process in result:
        assert isinstance(
            process["pid"],
            int,
        )

        assert process["pid"] > 0


def test_processes_with_services_counts_are_valid():
    result = get_processes_with_services()

    for process in result:
        assert process["services"] >= 0
        assert process["running"] >= 0
        assert process["stopped"] >= 0

        assert (
            process["running"]
            + process["stopped"]
            <= process["services"]
        )


def test_processes_with_services_service_list_matches_count():
    result = get_processes_with_services()

    for process in result:
        assert isinstance(
            process["service_list"],
            list,
        )

        assert len(
            process["service_list"]
        ) == process["services"]