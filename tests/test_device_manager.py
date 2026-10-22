import pytest

from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_manager import DeviceManager
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType


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


def test_manager_starts_empty():
    manager = DeviceManager()

    assert manager.count() == 0
    assert manager.get_devices() == []


def test_manager_can_add_device():
    manager = DeviceManager()
    device = create_device()

    manager.add_device(device)

    assert manager.count() == 1
    assert manager.get_device("device-001") is device


def test_manager_rejects_duplicate_device():
    manager = DeviceManager()

    manager.add_device(create_device())

    with pytest.raises(ValueError):
        manager.add_device(create_device())


def test_manager_can_get_devices():
    manager = DeviceManager()

    device_1 = create_device("device-001", "PC-01")
    device_2 = create_device("device-002", "PC-02")

    manager.add_device(device_1)
    manager.add_device(device_2)

    devices = manager.get_devices()

    assert len(devices) == 2
    assert device_1 in devices
    assert device_2 in devices


def test_manager_returns_none_for_unknown_device():
    manager = DeviceManager()

    assert manager.get_device("unknown") is None


def test_manager_can_remove_device():
    manager = DeviceManager()
    device = create_device()

    manager.add_device(device)

    removed = manager.remove_device("device-001")

    assert removed is True
    assert manager.count() == 0
    assert manager.get_device("device-001") is None


def test_manager_remove_unknown_device():
    manager = DeviceManager()

    assert manager.remove_device("unknown") is False


def test_manager_can_update_device():
    manager = DeviceManager()

    device = create_device()
    manager.add_device(device)

    updated_device = create_device(
        "device-001",
        "PC-ATUALIZADO",
    )

    manager.update_device(updated_device)

    result = manager.get_device("device-001")

    assert result is updated_device
    assert result.name == "PC-ATUALIZADO"


def test_manager_rejects_update_of_unknown_device():
    manager = DeviceManager()

    with pytest.raises(ValueError):
        manager.update_device(create_device())


def test_manager_can_clear_devices():
    manager = DeviceManager()

    manager.add_device(
        create_device("device-001", "PC-01")
    )

    manager.add_device(
        create_device("device-002", "PC-02")
    )

    manager.clear()

    assert manager.count() == 0
    assert manager.get_devices() == []