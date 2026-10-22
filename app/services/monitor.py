import time

import psutil

from app.core.config import MONITOR_INTERVALS
from app.data.interfaces.control_source import ControlSource
from app.data.interfaces.data_source import DataSource
from app.data.models.device import Device
from app.data.sources.factory import SourceFactory
from app.services.service_process import (
    get_service_process_network,
)


class SystemMonitor:
    """
    Camada central de monitoramento do SysView.

    O monitor controla:
    - cache;
    - frequência de atualização;
    - correlação entre dados;
    - acesso à fonte de dados;
    - acesso à fonte de controle;
    - dispositivo associado ao monitor.

    A coleta propriamente dita fica na DataSource.
    As ações de controle ficam na ControlSource.
    """

    def __init__(
        self,
        data_source: DataSource | None = None,
        control_source: ControlSource | None = None,
        device: Device | None = None,
    ):
        self.device = device

        if data_source is not None:
            self.data_source = data_source
        elif device is not None:
            self.data_source = SourceFactory.create_data_source(
                device
            )
        else:
            self.data_source = None

        if control_source is not None:
            self.control_source = control_source
        elif device is not None:
            self.control_source = SourceFactory.create_control_source(
                device
            )
        else:
            self.control_source = None

        self.dashboard_cache = None
        self.network_cache = None
        self.network_connections_cache = None
        self.process_cache = None
        self.process_network_cache = None
        self.process_services_cache = None
        self.services_cache = None
        self.system_cache = None

        self.last_dashboard_update = 0.0
        self.last_network_update = 0.0
        self.last_network_connections_update = 0.0
        self.last_process_update = 0.0
        self.last_process_network_update = 0.0
        self.last_process_services_update = 0.0
        self.last_services_update = 0.0
        self.last_system_update = 0.0

        self.dashboard_interval = MONITOR_INTERVALS["dashboard"]
        self.network_interval = MONITOR_INTERVALS["network"]
        self.network_connections_interval = (
            MONITOR_INTERVALS["network_connections"]
        )
        self.process_interval = MONITOR_INTERVALS["process"]
        self.process_network_interval = (
            MONITOR_INTERVALS["process_network"]
        )
        self.process_services_interval = (
            MONITOR_INTERVALS["process_services"]
        )
        self.services_interval = MONITOR_INTERVALS["services"]
        self.system_interval = MONITOR_INTERVALS["system"]

    def set_device(self, device: Device) -> None:
        self.device = device

    def get_device(self) -> Device | None:
        return self.device

    def get_device_info(self) -> dict | None:
        if self.device is None:
            return None

        return self.device.get_source_info()

    def get_source_info(self) -> dict:
        if self.data_source is None:
            return {}

        return self.data_source.get_source_info()

    @staticmethod
    def _is_cache_valid(
        cache,
        last_update: float,
        interval: float,
    ) -> bool:
        if cache is None:
            return False

        elapsed = time.monotonic() - last_update

        return elapsed < interval

    @staticmethod
    def _clear_cache(
        cache_name: str,
        last_update_name: str,
        instance,
    ) -> None:
        setattr(instance, cache_name, None)
        setattr(instance, last_update_name, 0.0)

    def get_dashboard(self) -> dict:
        if self.data_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de dados."
            )

        if not self._is_cache_valid(
            self.dashboard_cache,
            self.last_dashboard_update,
            self.dashboard_interval,
        ):
            self.dashboard_cache = self.data_source.get_dashboard()
            self.last_dashboard_update = time.monotonic()

        return self.dashboard_cache

    def get_cpu(self) -> dict:
        dashboard = self.get_dashboard()
        return dashboard["cpu"]

    def get_memory(self) -> dict:
        dashboard = self.get_dashboard()
        return dashboard["memory"]

    def get_disk(self) -> dict:
        dashboard = self.get_dashboard()
        return dashboard["disk"]

    def get_network(self) -> dict:
        if self.data_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de dados."
            )

        if not self._is_cache_valid(
            self.network_cache,
            self.last_network_update,
            self.network_interval,
        ):
            self.network_cache = self.data_source.get_network()
            self.last_network_update = time.monotonic()

        return self.network_cache

    def get_network_connections(self) -> list[dict]:
        if self.data_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de dados."
            )

        if not self._is_cache_valid(
            self.network_connections_cache,
            self.last_network_connections_update,
            self.network_connections_interval,
        ):
            self.network_connections_cache = (
                self.data_source.get_network_connections()
            )
            self.last_network_connections_update = time.monotonic()

        return self.network_connections_cache

    def get_processes(self) -> list[dict]:
        if self.data_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de dados."
            )

        if not self._is_cache_valid(
            self.process_cache,
            self.last_process_update,
            self.process_interval,
        ):
            self.process_cache = self.data_source.get_processes()
            self.last_process_update = time.monotonic()

        return self.process_cache

    def _build_process_network_data(
        self,
        connections: list[dict],
    ) -> list[dict]:
        grouped: dict[int, list[dict]] = {}

        for connection in connections:
            pid = connection.get("pid")

            if pid is None:
                continue

            try:
                pid = int(pid)
            except (TypeError, ValueError):
                continue

            if pid <= 0:
                continue

            grouped.setdefault(pid, []).append(connection)

        processes = []

        for pid, process_connections in grouped.items():
            try:
                process = psutil.Process(pid)
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

            try:
                process_name = process.name()
            except psutil.AccessDenied:
                process_name = "Acesso negado"

            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "Acesso negado"

            try:
                exe = process.exe()
            except psutil.AccessDenied:
                exe = "Acesso negado"

            tcp = 0
            udp = 0
            established = 0
            listening = 0

            for connection in process_connections:
                protocol = connection.get("protocol")
                status = connection.get("status")

                if protocol == "TCP":
                    tcp += 1
                elif protocol == "UDP":
                    udp += 1

                if status == "ESTABLISHED":
                    established += 1
                elif status == "LISTEN":
                    listening += 1

            processes.append(
                {
                    "pid": pid,
                    "process": process_name,
                    "username": username,
                    "exe": exe,
                    "connections": len(process_connections),
                    "tcp": tcp,
                    "udp": udp,
                    "established": established,
                    "listening": listening,
                }
            )

        processes.sort(
            key=lambda item: (
                item["connections"],
                item["process"] or "",
            ),
            reverse=True,
        )

        return processes

    def get_processes_with_network(self) -> list[dict]:
        if not self._is_cache_valid(
            self.process_network_cache,
            self.last_process_network_update,
            self.process_network_interval,
        ):
            connections = self.get_network_connections()

            self.process_network_cache = (
                self._build_process_network_data(
                    connections
                )
            )

            self.last_process_network_update = time.monotonic()

        return self.process_network_cache

    def _build_process_services_data(
        self,
        services: list[dict],
    ) -> list[dict]:
        services_by_pid: dict[int, list[dict]] = {}

        for service in services:
            pid = service.get("pid")

            if pid is None:
                continue

            try:
                pid = int(pid)
            except (TypeError, ValueError):
                continue

            if pid <= 0:
                continue

            services_by_pid.setdefault(pid, []).append(service)

        processes = []

        for pid, process_services in services_by_pid.items():
            try:
                process = psutil.Process(pid)
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

            try:
                process_name = process.name()
            except psutil.AccessDenied:
                process_name = "Acesso negado"

            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "Acesso negado"

            try:
                exe = process.exe()
            except psutil.AccessDenied:
                exe = "Acesso negado"

            running = 0
            stopped = 0
            other = 0

            for service in process_services:
                status = str(
                    service.get("status") or ""
                ).lower()

                if status == "running":
                    running += 1
                elif status == "stopped":
                    stopped += 1
                else:
                    other += 1

            processes.append(
                {
                    "pid": pid,
                    "process": process_name,
                    "username": username,
                    "exe": exe,
                    "services": len(process_services),
                    "running": running,
                    "stopped": stopped,
                    "other": other,
                    "service_list": process_services,
                }
            )

        processes.sort(
            key=lambda item: (
                item["services"],
                item["process"] or "",
            ),
            reverse=True,
        )

        return processes

    def get_processes_with_services(self) -> list[dict]:
        if not self._is_cache_valid(
            self.process_services_cache,
            self.last_process_services_update,
            self.process_services_interval,
        ):
            services = self.get_services()

            self.process_services_cache = (
                self._build_process_services_data(
                    services
                )
            )

            self.last_process_services_update = time.monotonic()

        return self.process_services_cache

    def get_services(self) -> list[dict]:
        if self.data_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de dados."
            )

        if not self._is_cache_valid(
            self.services_cache,
            self.last_services_update,
            self.services_interval,
        ):
            self.services_cache = self.data_source.get_services()
            self.last_services_update = time.monotonic()

        return self.services_cache

    def get_service_process_network(
        self,
        service: dict,
    ) -> dict:
        connections = self.get_network_connections()

        return get_service_process_network(
            service,
            connections,
        )

    def _require_control_source(self) -> ControlSource:
        if self.control_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de controle."
            )

        return self.control_source

    def lock_computer(self) -> None:
        self._require_control_source().lock_computer()

    def shutdown_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        self._require_control_source().shutdown_computer(
            delay_seconds=delay_seconds,
        )

    def restart_computer(
        self,
        delay_seconds: int = 30,
    ) -> None:
        self._require_control_source().restart_computer(
            delay_seconds=delay_seconds,
        )

    def cancel_shutdown(self) -> None:
        self._require_control_source().cancel_shutdown()

    def start_service(
        self,
        service_name: str,
    ) -> None:
        self._require_control_source().start_service(
            service_name
        )

    def stop_service(
        self,
        service_name: str,
    ) -> None:
        self._require_control_source().stop_service(
            service_name
        )

    def restart_service(
        self,
        service_name: str,
    ) -> None:
        self._require_control_source().restart_service(
            service_name
        )

    def get_system(self) -> dict:
        if self.data_source is None:
            raise RuntimeError(
                "O monitor não possui uma fonte de dados."
            )

        if not self._is_cache_valid(
            self.system_cache,
            self.last_system_update,
            self.system_interval,
        ):
            self.system_cache = self.data_source.get_system()
            self.last_system_update = time.monotonic()

        return self.system_cache

    def _invalidate_process_network_cache(self):
        self.process_network_cache = None
        self.last_process_network_update = 0.0

    def _invalidate_process_services_cache(self):
        self.process_services_cache = None
        self.last_process_services_update = 0.0

    def _invalidate_network_connections_cache(self):
        self.network_connections_cache = None
        self.last_network_connections_update = 0.0
        self._invalidate_process_network_cache()

    def _invalidate_services_cache(self):
        self.services_cache = None
        self.last_services_update = 0.0
        self._invalidate_process_services_cache()

    def force_refresh_processes(self):
        self._clear_cache(
            "process_cache",
            "last_process_update",
            self,
        )

        return self.get_processes()

    def force_refresh_process_network(self):
        self._invalidate_network_connections_cache()

        return self.get_processes_with_network()

    def force_refresh_process_services(self):
        self._invalidate_services_cache()

        return self.get_processes_with_services()

    def force_refresh_services(self):
        self._invalidate_services_cache()

        return self.get_services()

    def force_refresh_network(self):
        self._clear_cache(
            "network_cache",
            "last_network_update",
            self,
        )

        return self.get_network()

    def force_refresh_network_connections(self):
        self._invalidate_network_connections_cache()

        return self.get_network_connections()

    def force_refresh_system(self):
        self._clear_cache(
            "system_cache",
            "last_system_update",
            self,
        )

        return self.get_system()

    def force_refresh_dashboard(self):
        self._clear_cache(
            "dashboard_cache",
            "last_dashboard_update",
            self,
        )

        return self.get_dashboard()

    def force_refresh_all(self) -> dict:
        self.dashboard_cache = None
        self.network_cache = None
        self.network_connections_cache = None
        self.process_cache = None
        self.process_network_cache = None
        self.process_services_cache = None
        self.services_cache = None
        self.system_cache = None

        self.last_dashboard_update = 0.0
        self.last_network_update = 0.0
        self.last_network_connections_update = 0.0
        self.last_process_update = 0.0
        self.last_process_network_update = 0.0
        self.last_process_services_update = 0.0
        self.last_services_update = 0.0
        self.last_system_update = 0.0

        return self.get_all_data()

    def get_all_data(self) -> dict:
        dashboard = self.get_dashboard()

        return {
            "cpu": dashboard["cpu"],
            "memory": dashboard["memory"],
            "disk": dashboard["disk"],
            "network": self.get_network(),
            "network_connections": self.get_network_connections(),
            "processes": self.get_processes(),
            "processes_with_network": self.get_processes_with_network(),
            "processes_with_services": self.get_processes_with_services(),
            "services": self.get_services(),
            "system": self.get_system(),
        }


monitor = SystemMonitor()


def get_dashboard_data() -> dict:
    return monitor.get_dashboard()


def get_network_data() -> list[dict]:
    return monitor.get_network()["interfaces"]


def get_network_traffic_data() -> dict:
    return monitor.get_network()["traffic"]


def get_network_speed_data() -> dict:
    return monitor.get_network()["speed"]


def get_network_connections_data() -> list[dict]:
    return monitor.get_network_connections()


def get_process_data() -> list[dict]:
    return monitor.get_processes()


def get_process_network_data() -> list[dict]:
    return monitor.get_processes_with_network()


def get_process_services_data() -> list[dict]:
    return monitor.get_processes_with_services()


def get_service_data() -> list[dict]:
    return monitor.get_services()


def get_service_process_network_data(
    service: dict,
) -> dict:
    return monitor.get_service_process_network(service)


def get_system_data() -> dict:
    return monitor.get_system()


def get_monitor_data() -> dict:
    return monitor.get_all_data()