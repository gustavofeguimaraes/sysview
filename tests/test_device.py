from datetime import datetime

from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType


def test_device_creation():
    device = Device(
        device_id="device-001",
        name="PC-TESTE",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.LOCAL,
    )

    assert device.device_id == "device-001"
    assert device.name == "PC-TESTE"
    assert device.device_type == DeviceType.COMPUTER
    assert device.platform == PlatformType.WINDOWS
    assert device.connection_type == ConnectionType.LOCAL
    assert device.online is False


def test_device_can_store_network_address():
    device = Device(
        device_id="device-002",
        name="PC-TESTE",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.REMOTE,
        address="192.168.1.100",
        port=8765,
    )

    assert device.address == "192.168.1.100"
    assert device.port == 8765


def test_device_can_mark_online():
    device = Device(
        device_id="device-003",
        name="ANDROID-TESTE",
        device_type=DeviceType.MOBILE,
        platform=PlatformType.ANDROID,
        connection_type=ConnectionType.REMOTE,
    )

    device.mark_online()

    assert device.online is True
    assert isinstance(device.last_seen, datetime)


def test_device_can_mark_offline():
    device = Device(
        device_id="device-004",
        name="PC-TESTE",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.LOCAL,
    )

    device.mark_online()
    device.mark_offline()

    assert device.online is False


def test_device_source_info():
    device = Device(
        device_id="device-005",
        name="PC-TESTE",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.REMOTE,
        address="192.168.1.50",
        port=8765,
    )

    info = device.get_source_info()

    assert info["device_id"] == "device-005"
    assert info["name"] == "PC-TESTE"
    assert info["device_type"] == "computer"
    assert info["platform"] == "windows"
    assert info["connection_type"] == "remote"
    assert info["address"] == "192.168.1.50"
    assert info["port"] == 8765
    assert info["online"] is False