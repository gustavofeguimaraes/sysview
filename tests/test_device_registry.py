from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_registry import DeviceRegistry
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType
from app.services.monitor import SystemMonitor


def create_device(
    device_id: str = "device-001",
    name: str = "PC-TESTE",
) -> Device:
    return Device(
        device_id=device_id,
        name=name,
        device_type=DeviceType.COMPUTER,
        platform=PlatformType.WINDOWS,
        connection_type=ConnectionType.LOCAL,
    )


def test_registry_starts_empty():
    registry = DeviceRegistry()

    assert registry.count() == 0
    assert registry.get_devices() == []


def test_registry_registers_device():
    registry = DeviceRegistry()
    device = create_device()

    registry.register(device)

    assert registry.count() == 1
    assert registry.get_device("device-001") is device


def test_registry_creates_monitor_automatically():
    registry = DeviceRegistry()
    device = create_device()

    registry.register(device)

    monitor = registry.get_monitor("device-001")

    assert monitor is not None
    assert monitor.get_device() is device


def test_registry_accepts_custom_monitor():
    registry = DeviceRegistry()
    device = create_device()
    monitor = SystemMonitor()

    registry.register(device, monitor)

    assert registry.get_monitor("device-001") is monitor
    assert monitor.get_device() is device


def test_registry_rejects_duplicate_device():
    registry = DeviceRegistry()
    device = create_device()

    registry.register(device)

    try:
        registry.register(device)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "O registro deveria rejeitar dispositivos duplicados."
        )


def test_registry_can_check_device():
    registry = DeviceRegistry()
    device = create_device()

    registry.register(device)

    assert registry.contains("device-001") is True
    assert registry.contains("unknown") is False


def test_registry_can_remove_device():
    registry = DeviceRegistry()
    device = create_device()

    registry.register(device)

    removed = registry.remove("device-001")

    assert removed is True
    assert registry.count() == 0
    assert registry.get_device("device-001") is None
    assert registry.get_monitor("device-001") is None


def test_registry_remove_unknown_device():
    registry = DeviceRegistry()

    assert registry.remove("unknown") is False


def test_registry_can_list_monitors():
    registry = DeviceRegistry()

    device_1 = create_device("device-001", "PC-01")
    device_2 = create_device("device-002", "PC-02")

    registry.register(device_1)
    registry.register(device_2)

    monitors = registry.get_monitors()

    assert len(monitors) == 2


def test_registry_can_clear():
    registry = DeviceRegistry()

    registry.register(
        create_device("device-001", "PC-01")
    )

    registry.register(
        create_device("device-002", "PC-02")
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.get_devices() == []
    assert registry.get_monitors() == []