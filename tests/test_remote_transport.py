import pytest

from app.data.sources.remote_transport import RemoteTransport


def test_remote_transport_stores_connection_data():
    transport = RemoteTransport(
        host="192.168.1.100",
        port=8765,
        timeout=10,
    )

    assert transport.host == "192.168.1.100"
    assert transport.port == 8765
    assert transport.timeout == 10


def test_remote_transport_rejects_wrong_request_id(
    monkeypatch,
):
    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def sendall(self, data):
            pass

        def recv(self, size):
            return (
                b'{"version":1,'
                b'"type":"response",'
                b'"request_id":"wrong",'
                b'"success":true,'
                b'"payload":{}}'
            )

    def fake_create_connection(*args, **kwargs):
        return FakeSocket()

    monkeypatch.setattr(
        "socket.create_connection",
        fake_create_connection,
    )

    transport = RemoteTransport(
        host="127.0.0.1",
    )

    with pytest.raises(RuntimeError):
        transport.send_request(
            action="ping",
            request_id="correct",
        )