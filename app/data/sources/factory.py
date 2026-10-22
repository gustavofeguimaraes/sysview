from app.data.interfaces.control_source import ControlSource
from app.data.interfaces.data_source import DataSource
from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.platform_type import PlatformType
from app.data.sources.local import LocalDataSource
from app.data.sources.local_control import LocalControlSource
from app.data.sources.remote_windows import (
    RemoteWindowsControlSource,
    RemoteWindowsDataSource,
)


class SourceFactory:
    """
    Cria as fontes de dados e controle adequadas
    para cada dispositivo.

    A escolha é baseada na plataforma e no tipo
    de conexão.
    """

    @staticmethod
    def create_data_source(
        device: Device,
    ) -> DataSource:

        if (
            device.platform == PlatformType.WINDOWS
            and device.connection_type == ConnectionType.LOCAL
        ):
            return LocalDataSource()

        if (
            device.platform == PlatformType.WINDOWS
            and device.connection_type == ConnectionType.REMOTE
        ):
            if not device.address:
                raise ValueError(
                    "Um dispositivo Windows remoto precisa "
                    "ter um endereço configurado."
                )

            return RemoteWindowsDataSource(
                host=device.address,
                port=device.port or 8765,
            )

        if (
            device.platform == PlatformType.ANDROID
            and device.connection_type == ConnectionType.REMOTE
        ):
            raise NotImplementedError(
                "A fonte de dados para Android "
                "ainda não foi implementada."
            )

        raise NotImplementedError(
            "Não existe uma fonte de dados implementada "
            "para esta plataforma e tipo de conexão."
        )

    @staticmethod
    def create_control_source(
        device: Device,
    ) -> ControlSource:

        if (
            device.platform == PlatformType.WINDOWS
            and device.connection_type == ConnectionType.LOCAL
        ):
            return LocalControlSource()

        if (
            device.platform == PlatformType.WINDOWS
            and device.connection_type == ConnectionType.REMOTE
        ):
            return RemoteWindowsControlSource()

        if (
            device.platform == PlatformType.ANDROID
            and device.connection_type == ConnectionType.REMOTE
        ):
            raise NotImplementedError(
                "A fonte de controle para Android "
                "ainda não foi implementada."
            )

        raise NotImplementedError(
            "Não existe uma fonte de controle implementada "
            "para esta plataforma e tipo de conexão."
        )