
import logging

from app.data.interfaces.control_source import ControlSource

from app.services.computer_actions import (
    cancel_shutdown,
    lock_workstation,
    restart_computer,
    shutdown_computer,
)
from app.services.processes import terminate_process
from app.services.windows_services import (
    restart_service,
    start_service,
    stop_service,
)


logger = logging.getLogger(__name__)


class LocalControlSource(ControlSource):
    """
    Fonte de controle para o computador local.

    Responsável por encaminhar comandos para os
    serviços do sistema operacional.

    Operações administrativas podem exigir
    permissões elevadas do Windows.
    """

    @staticmethod
    def _validate_service_name(service_name: str) -> str:
        if not isinstance(service_name, str):
            raise ValueError(
                "O nome do serviço deve ser uma string."
            )

        service_name = service_name.strip()

        if not service_name:
            raise ValueError(
                "Informe um nome de serviço válido."
            )

        return service_name

    def lock_computer(self) -> None:
        logger.info("Solicitando bloqueio da estação")
        lock_workstation()

    def shutdown_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        logger.info(
            "Solicitando desligamento em %s segundos",
            delay_seconds,
        )

        shutdown_computer(
            delay_seconds=delay_seconds,
        )

    def restart_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        logger.info(
            "Solicitando reinicialização em %s segundos",
            delay_seconds,
        )

        restart_computer(
            delay_seconds=delay_seconds,
        )

    def cancel_shutdown(self) -> None:
        logger.info(
            "Solicitando cancelamento do desligamento"
        )
        cancel_shutdown()

    def start_service(
        self,
        service_name: str,
    ) -> bool:
        service_name = self._validate_service_name(
            service_name
        )

        logger.info(
            "Solicitando inicialização do serviço: %s",
            service_name,
        )

        return start_service(service_name)

    def stop_service(
        self,
        service_name: str,
    ) -> bool:
        service_name = self._validate_service_name(
            service_name
        )

        logger.info(
            "Solicitando parada do serviço: %s",
            service_name,
        )

        return stop_service(service_name)

    def restart_service(
        self,
        service_name: str,
    ) -> bool:
        service_name = self._validate_service_name(
            service_name
        )

        logger.info(
            "Solicitando reinicialização do serviço: %s",
            service_name,
        )

        return restart_service(service_name)

    def terminate_process(
        self,
        pid: int,
    ) -> bool:
        if not isinstance(pid, int) or pid <= 0:
            raise ValueError(
                "Informe um PID válido."
            )

        logger.info(
            "Solicitando encerramento do processo PID %s",
            pid,
        )

        return terminate_process(pid)
