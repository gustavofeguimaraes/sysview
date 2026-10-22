from app.services.service_process import (
    _build_network_summary,
    _get_process_connections,
    get_service_process_network_by_pid,
)


def test_get_process_connections():
    connections = [
        {
            "pid": 100,
            "protocol": "TCP",
            "local_port": 80,
        },
        {
            "pid": 200,
            "protocol": "TCP",
            "local_port": 443,
        },
        {
            "pid": 100,
            "protocol": "UDP",
            "local_port": 53,
        },
    ]

    result = _get_process_connections(
        100,
        connections,
    )

    assert len(result) == 2
    assert result[0]["pid"] == 100
    assert result[1]["pid"] == 100


def test_build_network_summary():
    connections = [
        {
            "protocol": "TCP",
            "status": "LISTEN",
            "local_port": 80,
            "remote_address": "*",
        },
        {
            "protocol": "TCP",
            "status": "ESTABLISHED",
            "local_port": 443,
            "remote_address": "192.168.1.10",
        },
        {
            "protocol": "UDP",
            "status": "NONE",
            "local_port": 53,
            "remote_address": "8.8.8.8",
        },
    ]

    result = _build_network_summary(
        connections
    )

    assert result["total_connections"] == 3
    assert result["tcp_connections"] == 2
    assert result["udp_connections"] == 1
    assert result["listening"] == 1
    assert result["established"] == 1

    assert 80 in result["local_ports"]
    assert 443 in result["local_ports"]
    assert 53 in result["local_ports"]

    assert "192.168.1.10" in result[
        "remote_addresses"
    ]

    assert "8.8.8.8" in result[
        "remote_addresses"
    ]


def test_build_network_summary_empty():
    result = _build_network_summary([])

    assert result["total_connections"] == 0
    assert result["tcp_connections"] == 0
    assert result["udp_connections"] == 0
    assert result["listening"] == 0
    assert result["established"] == 0
    assert result["local_ports"] == []
    assert result["remote_addresses"] == []


def test_get_service_process_network_by_pid_invalid_pid():
    result = get_service_process_network_by_pid(
        "abc",
        connections=[],
    )

    assert result["process"] is None
    assert result["connections"] == []

    assert result["network"]["total_connections"] == 0

    assert result["network"]["tcp_connections"] == 0

    assert result["network"]["udp_connections"] == 0


def test_get_service_process_network_by_pid_without_connections():
    result = get_service_process_network_by_pid(
        999999999,
        connections=[],
    )

    assert result["connections"] == []

    assert result["network"]["total_connections"] == 0