import socket
import threading
import time

from app.agent.server import AgentServer
from app.data.sources.remote_windows import (
    RemoteWindowsDataSource,
)


HOST = "127.0.0.1"
PORT = 18766


def start_test_server() -> AgentServer:
    server = AgentServer(
        host=HOST,
        port=PORT,
    )

    thread = threading.Thread(
        target=server.start,
        daemon=True,
    )

    thread.start()

    for _ in range(50):
        try:
            with socket.create_connection(
                (HOST, PORT),
                timeout=0.1,
            ):
                return server
        except OSError:
            time.sleep(0.05)

    server.stop()

    raise RuntimeError(
        "O Agent de teste não iniciou."
    )


def test_remote_windows_get_system():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        system_info = source.get_system()

        assert isinstance(system_info, dict)
        assert "platform" in system_info
        assert "hostname" in system_info
        assert system_info["platform"]
        assert system_info["hostname"]

    finally:
        server.stop()


def test_remote_windows_get_cpu():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        cpu = source.get_cpu()

        assert isinstance(cpu, dict)
        assert "usage_percent" in cpu
        assert "physical_cores" in cpu
        assert "logical_cores" in cpu

        assert 0 <= cpu["usage_percent"] <= 100

    finally:
        server.stop()


def test_remote_windows_get_memory():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        memory = source.get_memory()

        assert isinstance(memory, dict)
        assert "total_gb" in memory
        assert "available_gb" in memory
        assert "used_gb" in memory
        assert "usage_percent" in memory

        assert memory["total_gb"] > 0
        assert 0 <= memory["usage_percent"] <= 100

    finally:
        server.stop()


def test_remote_windows_get_disk():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        disk = source.get_disk()

        assert isinstance(disk, dict)
        assert "total_gb" in disk
        assert "used_gb" in disk
        assert "free_gb" in disk
        assert "usage_percent" in disk

        assert disk["total_gb"] > 0
        assert 0 <= disk["usage_percent"] <= 100

    finally:
        server.stop()


def test_remote_windows_get_dashboard():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        dashboard = source.get_dashboard()

        assert isinstance(dashboard, dict)

        assert "cpu" in dashboard
        assert "memory" in dashboard
        assert "disk" in dashboard

        assert "usage_percent" in dashboard["cpu"]
        assert "usage_percent" in dashboard["memory"]
        assert "usage_percent" in dashboard["disk"]

    finally:
        server.stop()


def test_remote_windows_get_network():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        network = source.get_network()

        assert isinstance(network, dict)

        assert "interfaces" in network
        assert "traffic" in network
        assert "speed" in network

        assert isinstance(
            network["interfaces"],
            list,
        )

        assert isinstance(
            network["traffic"],
            dict,
        )

        assert isinstance(
            network["speed"],
            dict,
        )

    finally:
        server.stop()


def test_remote_windows_get_network_connections():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        connections = source.get_network_connections()

        assert isinstance(
            connections,
            list,
        )

        for connection in connections:
            assert isinstance(
                connection,
                dict,
            )

    finally:
        server.stop()


def test_remote_windows_get_processes():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        processes = source.get_processes()

        assert isinstance(
            processes,
            list,
        )

        for process in processes:
            assert isinstance(
                process,
                dict,
            )

    finally:
        server.stop()


def test_remote_windows_get_services():
    server = start_test_server()

    try:
        source = RemoteWindowsDataSource(
            host=HOST,
            port=PORT,
        )

        services = source.get_services()

        assert isinstance(
            services,
            list,
        )

        for service in services:
            assert isinstance(
                service,
                dict,
            )

    finally:
        server.stop()