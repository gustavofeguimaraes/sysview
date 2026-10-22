from abc import ABC, abstractmethod


class DataSource(ABC):
    @abstractmethod
    def get_dashboard(self) -> dict:
        pass

    @abstractmethod
    def get_network(self) -> dict:
        pass

    @abstractmethod
    def get_network_connections(self) -> list[dict]:
        pass

    @abstractmethod
    def get_processes(self) -> list[dict]:
        pass

    def get_process(
        self,
        pid: int,
    ) -> dict | None:
        raise NotImplementedError(
            "A consulta individual de processos "
            "não está implementada nesta fonte de dados."
        )

    @abstractmethod
    def get_services(self) -> list[dict]:
        pass

    def get_service_process_network(
        self,
        service: dict,
    ) -> dict:
        raise NotImplementedError(
            "A consulta do processo e da rede do serviço "
            "não está implementada nesta fonte de dados."
        )

    @abstractmethod
    def get_system(self) -> dict:
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        pass

    def get_source_info(self) -> dict:
        return {
            "type": self.get_source_type(),
            "name": self.get_source_name(),
        }