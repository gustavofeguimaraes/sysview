
import logging

from app.data.models.device import Device


logger = logging.getLogger(__name__)


class DeviceManager:
    """
    Gerencia os dispositivos conhecidos pelo SysView.

    Funciona em dois modos:

    1. Memória:
       DeviceManager()

    2. Persistência:
       DeviceManager(repository=DeviceRepository())

    Quando um repositório é informado, os dispositivos
    são carregados do banco automaticamente.
    """

    def __init__(
        self,
        repository=None,
        auto_load: bool = True,
    ) -> None:
        self._devices: dict[str, Device] = {}
        self._repository = repository

        if self._repository is not None and auto_load:
            self.load_devices()

    def load_devices(self) -> int:
        """
        Carrega os dispositivos do repositório.

        Se não houver repositório, mantém os dispositivos
        atuais em memória.
        """
        if self._repository is None:
            return len(self._devices)

        devices = self._repository.get_all()

        loaded: dict[str, Device] = {}

        for device in devices:
            if device.device_id in loaded:
                raise ValueError(
                    f"Dispositivo duplicado no banco: "
                    f"'{device.device_id}'."
                )

            loaded[device.device_id] = device

        self._devices = loaded

        logger.info(
            "%d dispositivo(s) carregado(s).",
            len(self._devices),
        )

        return len(self._devices)

    def add_device(self, device: Device) -> None:
        """
        Cadastra um dispositivo.

        Com repositório, salva primeiro no banco.
        """
        if device.device_id in self._devices:
            raise ValueError(
                f"O dispositivo '{device.device_id}' "
                "já está cadastrado."
            )

        if self._repository is not None:
            created = self._repository.create(device)

            if not created:
                raise RuntimeError(
                    "O banco não confirmou o cadastro "
                    f"do dispositivo '{device.device_id}'."
                )

        self._devices[device.device_id] = device

        logger.info(
            "Dispositivo cadastrado: %s",
            device.device_id,
        )

    def get_device(
        self,
        device_id: str,
    ) -> Device | None:
        return self._devices.get(device_id)

    def get_devices(self) -> list[Device]:
        return list(self._devices.values())

    def remove_device(
        self,
        device_id: str,
    ) -> bool:
        """
        Remove um dispositivo.

        Com repositório, remove primeiro do banco.
        """
        if device_id not in self._devices:
            return False

        if self._repository is not None:
            deleted = self._repository.delete(device_id)

            if not deleted:
                raise RuntimeError(
                    "O banco não confirmou a exclusão "
                    f"do dispositivo '{device_id}'."
                )

        del self._devices[device_id]

        logger.info(
            "Dispositivo removido: %s",
            device_id,
        )

        return True

    def update_device(
        self,
        device: Device,
    ) -> None:
        """
        Atualiza um dispositivo existente.

        Com repositório, atualiza primeiro no banco.
        """
        if device.device_id not in self._devices:
            raise ValueError(
                f"O dispositivo '{device.device_id}' "
                "não está cadastrado."
            )

        if self._repository is not None:
            updated = self._repository.update(device)

            if not updated:
                raise RuntimeError(
                    "O banco não confirmou a atualização "
                    f"do dispositivo '{device.device_id}'."
                )

        self._devices[device.device_id] = device

        logger.info(
            "Dispositivo atualizado: %s",
            device.device_id,
        )

    def clear(self) -> None:
        """
        Limpa apenas os dispositivos em memória.

        Nunca exclui registros do banco.
        """
        self._devices.clear()

        logger.info(
            "Cache de dispositivos limpo."
        )

    def count(self) -> int:
        return len(self._devices)
