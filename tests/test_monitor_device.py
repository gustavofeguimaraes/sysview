from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType
from app.services.monitor import SystemMonitor


def test_monitor_can_receive_device():
    device = Device(
        device_id="device-001",
        name="PC-TESTE",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.LOCAL,
    )

    monitor = SystemMonitor(device=device)

    assert monitor.get_device() is device


def test_monitor_can_set_device():
    monitor = SystemMonitor()

    device = Device(
        device_id="device-002",
        name="PC-TESTE",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.LOCAL,
    )

    monitor.set_device(device)

    assert monitor.get_device() is device


def test_monitor_without_device_returns_none():
    monitor = SystemMonitor()

    assert monitor.get_device() is None
    assert monitor.get_device_info() is None


def test_monitor_returns_device_info():
    device = Device(
        device_id="device-003",
        name="PC-GUSTAVO",
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.LOCAL,
        address="192.168.1.100",
        port=8765,
    )

    monitor = SystemMonitor(device=device)

    info = monitor.get_device_info()

    assert info["device_id"] == "device-003"
    assert info["name"] == "PC-GUSTAVO"
    assert info["device_type"] == "computer"
    assert info["platform"] == "windows"
    assert info["connection_type"] == "local"
    assert info["address"] == "192.168.1.100"
    assert info["port"] == 8765