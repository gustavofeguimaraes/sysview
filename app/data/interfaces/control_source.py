from abc import ABC, abstractmethod


class ControlSource(ABC):
    @abstractmethod
    def lock_computer(self) -> None:
        pass

    @abstractmethod
    def shutdown_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        pass

    @abstractmethod
    def restart_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        pass

    @abstractmethod
    def cancel_shutdown(self) -> None:
        pass

    @abstractmethod
    def start_service(
        self,
        service_name: str,
    ) -> None:
        pass

    @abstractmethod
    def stop_service(
        self,
        service_name: str,
    ) -> None:
        pass

    @abstractmethod
    def restart_service(
        self,
        service_name: str,
    ) -> None:
        pass

    def terminate_process(
        self,
        pid: int,
    ) -> bool:
        raise NotImplementedError(
            "A finalização de processos "
            "não está implementada nesta fonte de controle."
        )