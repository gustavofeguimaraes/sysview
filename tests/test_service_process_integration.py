import os

from app.services.service_process import (
    get_service_process_network_by_pid,
    get_services_processes_network,
)


def test_get_service_process_network_by_pid_current_process():
    pid = os.getpid()

    result = get_service_process_network_by_pid(pid)

    assert result is not None

    assert "process" in result
    assert "network" in result
    assert "connections" in result

    assert result["process"] is not None

    assert result["process"]["pid"] == pid

    assert isinstance(result["connections"], list)


def test_get_service_process_network_by_pid_network_structure():
    pid = os.getpid()

    result = get_service_process_network_by_pid(pid)

    assert result is not None

    network = result["network"]

    assert "total_connections" in network
    assert "tcp_connections" in network
    assert "udp_connections" in network
    assert "listening" in network
    assert "established" in network
    assert "local_ports" in network
    assert "remote_addresses" in network

    assert network["total_connections"] >= 0
    assert network["tcp_connections"] >= 0
    assert network["udp_connections"] >= 0
    assert network["listening"] >= 0
    assert network["established"] >= 0

    assert isinstance(network["local_ports"], list)
    assert isinstance(network["remote_addresses"], list)


def test_get_service_process_network_by_pid_invalid_pid():
    result = get_service_process_network_by_pid(
        999999999
    )

    assert result is not None

    assert result["process"] is None
    assert result["connections"] == []

    assert result["network"]["total_connections"] == 0


def test_get_services_processes_network_empty_list():
    result = get_services_processes_network([])

    assert isinstance(result, list)
    assert result == []


def test_get_services_processes_network_structure():
    services = [
        {
            "name": "TestService",
            "display_name": "Test Service",
            "status": "running",
            "start_type": "auto",
            "pid": os.getpid(),
        }
    ]

    result = get_services_processes_network(
        services
    )

    assert isinstance(result, list)
    assert len(result) == 1

    item = result[0]

    assert "service" in item
    assert "process" in item
    assert "network" in item
    assert "connections" in item

    assert item["service"]["name"] == "TestService"

    assert isinstance(
        item["connections"],
        list,
    )

    assert isinstance(
        item["network"],
        dict,
    )