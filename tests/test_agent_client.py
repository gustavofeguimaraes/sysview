import socket
import threading
import time

from app.agent.protocol import (
    create_request,
    decode_message,
    encode_message,
)
from app.agent.server import AgentServer


HOST = "127.0.0.1"
PORT = 18765


def start_test_server() -> AgentServer:
    server = AgentServer(
        host=HOST,
        port=PORT,
    )

    thread = threading.Thread(
        target=server.start,
        daemon=True,
    )

    thread.start()

    for _ in range(50):
        try:
            with socket.create_connection(
                (HOST, PORT),
                timeout=0.1,
            ):
                return server
        except OSError:
            time.sleep(0.05)

    server.stop()

    raise RuntimeError(
        "O Agent de teste não iniciou."
    )


def send_request(request: dict) -> dict:
    with socket.create_connection(
        (HOST, PORT),
        timeout=5,
    ) as client:

        client.sendall(
            encode_message(request)
        )

        data = client.recv(4096)

    return decode_message(data)


def test_agent_ping():
    server = start_test_server()

    try:
        request = create_request(
            action="ping",
            request_id="test-ping-001",
        )

        response = send_request(request)

        assert response["type"] == "response"
        assert response["request_id"] == "test-ping-001"
        assert response["success"] is True
        assert response["payload"]["message"] == "pong"

    finally:
        server.stop()


def test_agent_info():
    server = start_test_server()

    try:
        request = create_request(
            action="agent_info",
            request_id="test-info-001",
        )

        response = send_request(request)

        assert response["type"] == "response"
        assert response["request_id"] == "test-info-001"
        assert response["success"] is True
        assert response["payload"]["name"] == "SysView Agent"
        assert response["payload"]["version"] == "0.1.0"

    finally:
        server.stop()