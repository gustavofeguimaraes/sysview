from app.data.models.device import Device
from app.services.monitor import SystemMonitor


class DeviceRegistry:
    """
    Registro central de dispositivos do SysView.

    Responsável por manter os dispositivos conhecidos
    e seus respectivos monitores.
    """

    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}
        self._monitors: dict[str, SystemMonitor] = {}

    def register(
        self,
        device: Device,
        monitor: SystemMonitor | None = None,
    ) -> None:
        """
        Registra um dispositivo no SysView.

        Se nenhum monitor for informado, um novo
        SystemMonitor será criado automaticamente.
        """

        if device.device_id in self._devices:
            raise ValueError(
                f"O dispositivo '{device.device_id}' "
                "já está registrado."
            )

        if monitor is None:
            monitor = SystemMonitor(
                device=device,
            )
        else:
            monitor.set_device(device)

        self._devices[device.device_id] = device
        self._monitors[device.device_id] = monitor

    def get_device(
        self,
        device_id: str,
    ) -> Device | None:
        return self._devices.get(device_id)

    def get_monitor(
        self,
        device_id: str,
    ) -> SystemMonitor | None:
        return self._monitors.get(device_id)

    def get_devices(self) -> list[Device]:
        return list(self._devices.values())

    def get_monitors(self) -> list[SystemMonitor]:
        return list(self._monitors.values())

    def remove(
        self,
        device_id: str,
    ) -> bool:
        if device_id not in self._devices:
            return False

        del self._devices[device_id]
        del self._monitors[device_id]

        return True

    def contains(
        self,
        device_id: str,
    ) -> bool:
        return device_id in self._devices

    def count(self) -> int:
        return len(self._devices)

    def clear(self) -> None:
        self._devices.clear()
        self._monitors.clear()