from app.data.interfaces.control_source import ControlSource
from app.data.interfaces.data_source import DataSource
from app.services.monitor import SystemMonitor


class FakeDataSource(DataSource):
    def get_dashboard(self):
        return {
            "cpu": {"usage_percent": 10},
            "memory": {"usage_percent": 20},
            "disk": {"usage_percent": 30},
        }

    def get_network(self):
        return {
            "interfaces": [],
            "traffic": {},
            "speed": {},
        }

    def get_network_connections(self):
        return []

    def get_processes(self):
        return []

    def get_services(self):
        return []

    def get_system(self):
        return {
            "hostname": "TEST-PC",
        }

    def get_source_type(self):
        return "fake"

    def get_source_name(self):
        return "Fonte falsa"


class FakeControlSource(ControlSource):
    def __init__(self):
        self.last_action = None
        self.last_service = None
        self.last_delay = None

    def lock_computer(self):
        self.last_action = "lock"

    def shutdown_computer(
        self,
        delay_seconds=30,
    ):
        self.last_action = "shutdown"
        self.last_delay = delay_seconds

    def restart_computer(
        self,
        delay_seconds=30,
    ):
        self.last_action = "restart"
        self.last_delay = delay_seconds

    def cancel_shutdown(self):
        self.last_action = "cancel_shutdown"

    def start_service(
        self,
        service_name,
    ):
        self.last_action = "start_service"
        self.last_service = service_name

    def stop_service(
        self,
        service_name,
    ):
        self.last_action = "stop_service"
        self.last_service = service_name

    def restart_service(
        self,
        service_name,
    ):
        self.last_action = "restart_service"
        self.last_service = service_name


def test_monitor_accepts_custom_data_source():
    data_source = FakeDataSource()

    monitor = SystemMonitor(
        data_source=data_source,
    )

    assert monitor.get_source_info() == {
        "type": "fake",
        "name": "Fonte falsa",
    }


def test_monitor_uses_custom_dashboard_data():
    data_source = FakeDataSource()

    monitor = SystemMonitor(
        data_source=data_source,
    )

    result = monitor.get_dashboard()

    assert result["cpu"]["usage_percent"] == 10
    assert result["memory"]["usage_percent"] == 20
    assert result["disk"]["usage_percent"] == 30


def test_monitor_uses_custom_network_data():
    data_source = FakeDataSource()

    monitor = SystemMonitor(
        data_source=data_source,
    )

    result = monitor.get_network()

    assert result == {
        "interfaces": [],
        "traffic": {},
        "speed": {},
    }


def test_monitor_uses_custom_system_data():
    data_source = FakeDataSource()

    monitor = SystemMonitor(
        data_source=data_source,
    )

    result = monitor.get_system()

    assert result["hostname"] == "TEST-PC"


def test_monitor_accepts_custom_control_source():
    data_source = FakeDataSource()
    control_source = FakeControlSource()

    monitor = SystemMonitor(
        data_source=data_source,
        control_source=control_source,
    )

    assert monitor.control_source is control_source


def test_monitor_controls_computer_without_real_action():
    data_source = FakeDataSource()
    control_source = FakeControlSource()

    monitor = SystemMonitor(
        data_source=data_source,
        control_source=control_source,
    )

    monitor.lock_computer()

    assert control_source.last_action == "lock"


def test_monitor_controls_shutdown_without_real_action():
    data_source = FakeDataSource()
    control_source = FakeControlSource()

    monitor = SystemMonitor(
        data_source=data_source,
        control_source=control_source,
    )

    monitor.shutdown_computer(
        delay_seconds=15,
    )

    assert control_source.last_action == "shutdown"
    assert control_source.last_delay == 15


def test_monitor_controls_restart_without_real_action():
    data_source = FakeDataSource()
    control_source = FakeControlSource()

    monitor = SystemMonitor(
        data_source=data_source,
        control_source=control_source,
    )

    monitor.restart_computer(
        delay_seconds=20,
    )

    assert control_source.last_action == "restart"
    assert control_source.last_delay == 20


def test_monitor_controls_services_without_real_action():
    data_source = FakeDataSource()
    control_source = FakeControlSource()

    monitor = SystemMonitor(
        data_source=data_source,
        control_source=control_source,
    )

    monitor.start_service("Spooler")

    assert control_source.last_action == "start_service"
    assert control_source.last_service == "Spooler"

    monitor.stop_service("Spooler")

    assert control_source.last_action == "stop_service"
    assert control_source.last_service == "Spooler"

    monitor.restart_service("Spooler")

    assert control_source.last_action == "restart_service"
    assert control_source.last_service == "Spooler"


def test_monitor_can_cancel_shutdown_without_real_action():
    data_source = FakeDataSource()
    control_source = FakeControlSource()

    monitor = SystemMonitor(
        data_source=data_source,
        control_source=control_source,
    )

    monitor.cancel_shutdown()

    assert control_source.last_action == "cancel_shutdown"