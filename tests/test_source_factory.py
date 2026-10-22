import pytest

from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType
from app.data.sources.factory import SourceFactory
from app.data.sources.local import LocalDataSource
from app.data.sources.local_control import LocalControlSource


def create_windows_device(
    address: str | None = None,
    connection_type: ConnectionType = ConnectionType.LOCAL,
) -> Device:
    return Device(
        device_id="windows-001",
        name="PC-WINDOWS",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=connection_type,
        address=address,
    )


def test_factory_creates_local_data_source():
    device = create_windows_device()

    source = SourceFactory.create_data_source(device)

    assert isinstance(source, LocalDataSource)


def test_factory_creates_local_control_source():
    device = create_windows_device()

    source = SourceFactory.create_control_source(device)

    assert isinstance(source, LocalControlSource)


def test_factory_accepts_localhost():
    device = create_windows_device(
        address="localhost",
    )

    data_source = SourceFactory.create_data_source(device)
    control_source = SourceFactory.create_control_source(device)

    assert isinstance(data_source, LocalDataSource)
    assert isinstance(control_source, LocalControlSource)


def test_factory_accepts_loopback_address():
    device = create_windows_device(
        address="127.0.0.1",
    )

    data_source = SourceFactory.create_data_source(device)
    control_source = SourceFactory.create_control_source(device)

    assert isinstance(data_source, LocalDataSource)
    assert isinstance(control_source, LocalControlSource)


def test_factory_accepts_windows_network_address_for_now():
    device = create_windows_device(
        address="192.168.1.50",
        connection_type=ConnectionType.LOCAL,
    )

    data_source = SourceFactory.create_data_source(device)
    control_source = SourceFactory.create_control_source(device)

    assert isinstance(data_source, LocalDataSource)
    assert isinstance(control_source, LocalControlSource)


def test_factory_rejects_android_for_now():
    device = Device(
        device_id="android-001",
        name="CELULAR",
        device_type=DeviceType.MOBILE,
        platform=PlatformType.ANDROID,
        connection_type=ConnectionType.REMOTE,
    )

    with pytest.raises(NotImplementedError):
        SourceFactory.create_data_source(device)

    with pytest.raises(NotImplementedError):
        SourceFactory.create_control_source(device)