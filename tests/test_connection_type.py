from app.data.models.connection_type import ConnectionType


def test_local_connection_type():
    assert ConnectionType.LOCAL.value == "local"


def test_remote_connection_type():
    assert ConnectionType.REMOTE.value == "remote"


def test_connection_type_is_string_compatible():
    assert ConnectionType.LOCAL == "local"
    assert ConnectionType.REMOTE == "remote"