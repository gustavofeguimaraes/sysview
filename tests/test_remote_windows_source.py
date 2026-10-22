import pytest

from app.data.sources.remote_windows import (
    RemoteWindowsControlSource,
    RemoteWindowsDataSource,
)


HOST = "127.0.0.1"
PORT = 8765


def create_source() -> RemoteWindowsDataSource:
    return RemoteWindowsDataSource(
        host=HOST,
        port=PORT,
    )


def test_remote_windows_data_source_creation():
    source = create_source()

    assert source.host == HOST
    assert source.port == PORT
    assert source.transport.host == HOST
    assert source.transport.port == PORT


def test_remote_windows_data_source_source_type():
    source = create_source()

    assert source.get_source_type() == "remote_windows"


def test_remote_windows_data_source_source_name():
    source = create_source()

    assert source.get_source_name() == "Windows remoto"


def test_remote_windows_data_source_network_is_implemented():
    source = create_source()

    assert hasattr(source, "get_network")
    assert callable(source.get_network)


def test_remote_windows_data_source_network_connections_is_implemented():
    source = create_source()

    assert hasattr(source, "get_network_connections")
    assert callable(source.get_network_connections)


def test_remote_windows_data_source_processes_is_implemented():
    source = create_source()

    assert hasattr(source, "get_processes")
    assert callable(source.get_processes)


def test_remote_windows_data_source_services_is_implemented():
    source = create_source()

    assert hasattr(source, "get_services")
    assert callable(source.get_services)


def test_remote_windows_control_source_creation():
    source = RemoteWindowsControlSource()

    assert source is not None


def test_remote_windows_control_source_unimplemented_methods():
    source = RemoteWindowsControlSource()

    with pytest.raises(NotImplementedError):
        source.lock_computer()

    with pytest.raises(NotImplementedError):
        source.shutdown_computer()

    with pytest.raises(NotImplementedError):
        source.restart_computer()

    with pytest.raises(NotImplementedError):
        source.cancel_shutdown()

    with pytest.raises(NotImplementedError):
        source.start_service("TestService")

    with pytest.raises(NotImplementedError):
        source.stop_service("TestService")

    with pytest.raises(NotImplementedError):
        source.restart_service("TestService")