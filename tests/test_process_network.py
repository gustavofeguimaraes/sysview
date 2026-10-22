from app.services.process_network import (
    get_process_network_summary,
)


def test_process_network_summary_invalid_pid():
    result = get_process_network_summary(
        999999999
    )

    assert result is None


def test_process_network_summary_structure():
    import os

    pid = os.getpid()

    result = get_process_network_summary(
        pid
    )

    assert result is not None

    assert "pid" in result
    assert "process" in result
    assert "username" in result
    assert "exe" in result

    assert "total_connections" in result
    assert "tcp_connections" in result
    assert "udp_connections" in result
    assert "listening" in result
    assert "established" in result

    assert "local_ports" in result
    assert "remote_addresses" in result
    assert "connections" in result


def test_process_network_summary_counts_are_valid():
    import os

    pid = os.getpid()

    result = get_process_network_summary(
        pid
    )

    assert result is not None

    assert result["total_connections"] >= 0
    assert result["tcp_connections"] >= 0
    assert result["udp_connections"] >= 0
    assert result["listening"] >= 0
    assert result["established"] >= 0

    assert isinstance(
        result["local_ports"],
        list,
    )

    assert isinstance(
        result["remote_addresses"],
        list,
    )

    assert isinstance(
        result["connections"],
        list,
    )