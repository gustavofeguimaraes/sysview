import pytest

from app.data.interfaces.control_source import ControlSource


class CompleteControlSource(ControlSource):
    def lock_computer(self):
        pass

    def shutdown_computer(
        self,
        delay_seconds=30,
    ):
        pass

    def restart_computer(
        self,
        delay_seconds=30,
    ):
        pass

    def cancel_shutdown(self):
        pass

    def start_service(
        self,
        service_name,
    ):
        pass

    def stop_service(
        self,
        service_name,
    ):
        pass

    def restart_service(
        self,
        service_name,
    ):
        pass


def test_control_source_can_be_implemented():
    source = CompleteControlSource()

    assert isinstance(
        source,
        ControlSource,
    )


def test_control_source_requires_lock():
    class InvalidControlSource(ControlSource):
        def shutdown_computer(
            self,
            delay_seconds=30,
        ):
            pass

        def restart_computer(
            self,
            delay_seconds=30,
        ):
            pass

        def cancel_shutdown(self):
            pass

        def start_service(
            self,
            service_name,
        ):
            pass

        def stop_service(
            self,
            service_name,
        ):
            pass

        def restart_service(
            self,
            service_name,
        ):
            pass

    with pytest.raises(TypeError):
        InvalidControlSource()


def test_control_source_requires_service_actions():
    class InvalidControlSource(ControlSource):
        def lock_computer(self):
            pass

        def shutdown_computer(
            self,
            delay_seconds=30,
        ):
            pass

        def restart_computer(
            self,
            delay_seconds=30,
        ):
            pass

        def cancel_shutdown(self):
            pass

    with pytest.raises(TypeError):
        InvalidControlSource()