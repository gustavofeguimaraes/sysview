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


class LocalControlSource(ControlSource):
    def lock_computer(self) -> None:
        lock_workstation()

    def shutdown_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        shutdown_computer(
            delay_seconds=delay_seconds,
        )

    def restart_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        restart_computer(
            delay_seconds=delay_seconds,
        )

    def cancel_shutdown(self) -> None:
        cancel_shutdown()

    def start_service(
        self,
        service_name: str,
    ) -> None:
        start_service(service_name)

    def stop_service(
        self,
        service_name: str,
    ) -> None:
        stop_service(service_name)

    def restart_service(
        self,
        service_name: str,
    ) -> None:
        restart_service(service_name)

    def terminate_process(
        self,
        pid: int,
    ) -> bool:
        return terminate_process(pid)