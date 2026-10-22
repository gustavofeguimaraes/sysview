from app.data.interfaces.control_source import ControlSource
from app.data.sources.local_control import LocalControlSource


def test_local_control_source_implements_contract():
    source = LocalControlSource()

    assert isinstance(
        source,
        ControlSource,
    )


def test_local_control_source_has_computer_actions():
    source = LocalControlSource()

    assert callable(source.lock_computer)
    assert callable(source.shutdown_computer)
    assert callable(source.restart_computer)
    assert callable(source.cancel_shutdown)


def test_local_control_source_has_service_actions():
    source = LocalControlSource()

    assert callable(source.start_service)
    assert callable(source.stop_service)
    assert callable(source.restart_service)