from app.data.models.device import Device


class DeviceManager:
    """
    Gerencia os dispositivos conhecidos pelo SysView.

    Nesta etapa os dispositivos ficam apenas em memória.
    O armazenamento em MySQL será integrado posteriormente.
    """

    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}

    def add_device(self, device: Device) -> None:
        if device.device_id in self._devices:
            raise ValueError(
                f"O dispositivo '{device.device_id}' já está cadastrado."
            )

        self._devices[device.device_id] = device

    def get_device(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def get_devices(self) -> list[Device]:
        return list(self._devices.values())

    def remove_device(self, device_id: str) -> bool:
        if device_id not in self._devices:
            return False

        del self._devices[device_id]
        return True

    def update_device(self, device: Device) -> None:
        if device.device_id not in self._devices:
            raise ValueError(
                f"O dispositivo '{device.device_id}' não está cadastrado."
            )

        self._devices[device.device_id] = device

    def clear(self) -> None:
        self._devices.clear()

    def count(self) -> int:
        return len(self._devices)