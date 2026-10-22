from app.data.interfaces.data_source import DataSource

from app.services.dashboard import get_dashboard_snapshot
from app.services.network import (
    get_network_info,
    get_network_speed,
    get_network_traffic,
)
from app.services.network_connections import get_network_connections
from app.services.processes import (
    get_process,
    get_processes,
)
from app.services.service_process import (
    get_service_process_network,
)
from app.services.system_info import get_system_info
from app.services.windows_services import (
    get_windows_services,
)


class LocalDataSource(DataSource):
    def get_dashboard(self) -> dict:
        return get_dashboard_snapshot()

    def get_network(self) -> dict:
        return {
            "interfaces": get_network_info(),
            "traffic": get_network_traffic(),
            "speed": get_network_speed(),
        }

    def get_network_connections(self) -> list[dict]:
        return get_network_connections()

    def get_processes(self) -> list[dict]:
        return get_processes()

    def get_process(
        self,
        pid: int,
    ) -> dict | None:
        return get_process(pid)

    def get_services(self) -> list[dict]:
        return get_windows_services()

    def get_service_process_network(
        self,
        service: dict,
    ) -> dict:
        connections = self.get_network_connections()

        return get_service_process_network(
            service,
            connections,
        )

    def get_system(self) -> dict:
        return get_system_info()

    def get_source_type(self) -> str:
        return "local"

    def get_source_name(self) -> str:
        return "Computador local"