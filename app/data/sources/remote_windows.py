from app.data.interfaces.control_source import ControlSource
from app.data.interfaces.data_source import DataSource
from app.data.sources.remote_transport import RemoteTransport


class RemoteWindowsDataSource(DataSource):
    """
    Fonte de dados para um computador Windows remoto.

    A comunicação é feita através do SysView Agent.
    """

    def __init__(
        self,
        host: str,
        port: int = 8765,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port

        self.transport = RemoteTransport(
            host=host,
            port=port,
            timeout=timeout,
        )

    def get_dashboard(self) -> dict:
        return {
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
        }

    def get_cpu(self) -> dict:
        response = self.transport.send_request(
            action="cpu_info",
            request_id="cpu-info",
        )

        return response["payload"]

    def get_memory(self) -> dict:
        response = self.transport.send_request(
            action="memory_info",
            request_id="memory-info",
        )

        return response["payload"]

    def get_disk(self) -> dict:
        response = self.transport.send_request(
            action="disk_info",
            request_id="disk-info",
        )

        return response["payload"]

    def get_network(self) -> dict:
        response = self.transport.send_request(
            action="network_info",
            request_id="network-info",
        )

        return response["payload"]

    def get_network_connections(self) -> list[dict]:
        response = self.transport.send_request(
            action="network_connections",
            request_id="network-connections",
        )

        return response["payload"]["connections"]

    def get_processes(self) -> list[dict]:
        response = self.transport.send_request(
            action="processes",
            request_id="processes",
        )

        return response["payload"]["processes"]

    def get_process(
        self,
        pid: int,
    ) -> dict | None:
        response = self.transport.send_request(
            action="process_info",
            request_id=f"process-info-{pid}",
            payload={
                "pid": pid,
            },
        )

        return response["payload"].get(
            "process"
        )

    def get_services(self) -> list[dict]:
        response = self.transport.send_request(
            action="services",
            request_id="services",
        )

        return response["payload"]["services"]

    def get_service_process_network(
        self,
        service: dict,
    ) -> dict:
        raise NotImplementedError(
            "A consulta do processo e da rede de um serviço "
            "Windows remoto ainda não foi implementada."
        )

    def get_system(self) -> dict:
        response = self.transport.send_request(
            action="system_info",
            request_id="system-info",
        )

        return response["payload"]

    def get_source_type(self) -> str:
        return "remote_windows"

    def get_source_name(self) -> str:
        return "Windows remoto"


class RemoteWindowsControlSource(ControlSource):
    """
    Fonte de controle para um computador Windows remoto.
    """

    def _not_implemented(self) -> None:
        raise NotImplementedError(
            "O controle do Windows remoto ainda "
            "não foi implementado."
        )

    def lock_computer(self) -> None:
        self._not_implemented()

    def shutdown_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        self._not_implemented()

    def restart_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        self._not_implemented()

    def cancel_shutdown(self) -> None:
        self._not_implemented()

    def start_service(
        self,
        service_name: str,
    ) -> None:
        self._not_implemented()

    def stop_service(
        self,
        service_name: str,
    ) -> None:
        self._not_implemented()

    def restart_service(
        self,
        service_name: str,
    ) -> None:
        self._not_implemented()

    def terminate_process(
        self,
        pid: int,
    ) -> bool:
        self._not_implemented()