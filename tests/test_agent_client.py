
import socket
import threading
import time

import pytest

from app.agent.auth import (
    create_nonce,
    sign_request,
)
from app.agent.protocol import (
    create_request,
    decode_message,
    encode_message,
)
from app.agent.server import AgentServer


HOST = "127.0.0.1"
PORT = 18765

TEST_SECRET = "sysview-test-secret-0123456789-abcdef"


@pytest.fixture
def agent_server(monkeypatch):
    """
    Inicia o Agent com uma chave exclusiva de teste.
    Não utiliza a chave real do usuário.
    """
    monkeypatch.setenv(
        "SYSVIEW_AGENT_SECRET",
        TEST_SECRET,
    )

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
                break
        except OSError:
            time.sleep(0.05)
    else:
        server.stop()
        thread.join(timeout=2)

        raise RuntimeError(
            "O Agent de teste não iniciou."
        )

    try:
        yield server
    finally:
        server.stop()

        # Desbloqueia accept() caso ainda esteja aguardando.
        try:
            with socket.create_connection(
                (HOST, PORT),
                timeout=0.2,
            ):
                pass
        except OSError:
            pass

        thread.join(timeout=2)


def create_authenticated_request(
    action: str,
    request_id: str,
) -> dict:
    """
    Cria uma requisição assinada para os testes.
    """
    request = create_request(
        action=action,
        request_id=request_id,
    )

    request["timestamp"] = int(time.time())
    request["nonce"] = create_nonce()

    request["signature"] = sign_request(
        request,
        TEST_SECRET,
    )

    return request


def send_request(request: dict) -> dict:
    """
    Envia uma requisição TCP ao Agent de teste.
    """
    with socket.create_connection(
        (HOST, PORT),
        timeout=5,
    ) as client:

        client.sendall(
            encode_message(request)
        )

        data = client.recv(4096)

    return decode_message(data)


def test_agent_ping(agent_server):
    request = create_authenticated_request(
        action="ping",
        request_id="test-ping-001",
    )

    response = send_request(request)

    assert response["type"] == "response"
    assert response["request_id"] == "test-ping-001"
    assert response["success"] is True
    assert response["payload"]["message"] == "pong"


def test_agent_info(agent_server):
    request = create_authenticated_request(
        action="agent_info",
        request_id="test-info-001",
    )

    response = send_request(request)

    assert response["type"] == "response"
    assert response["request_id"] == "test-info-001"
    assert response["success"] is True
    assert response["payload"]["name"] == "SysView Agent"
    assert response["payload"]["version"] == "0.1.0"


def test_agent_rejects_unsigned_request(agent_server):
    """
    Requisições sem assinatura devem ser rejeitadas.
    """
    request = create_request(
        action="ping",
        request_id="test-unsigned-001",
    )

    response = send_request(request)

    assert response["success"] is False
    assert "Autenticação" in response["error"]


def test_agent_rejects_invalid_signature(agent_server):
    """
    Requisições com assinatura adulterada
    devem ser rejeitadas.
    """
    request = create_authenticated_request(
        action="ping",
        request_id="test-invalid-signature-001",
    )

    request["signature"] = "0" * 64

    response = send_request(request)

    assert response["success"] is False
    assert "Autenticação" in response["error"]


def test_agent_rejects_replayed_request(agent_server):
    """
    A mesma requisição não pode ser executada duas vezes.
    """
    request = create_authenticated_request(
        action="ping",
        request_id="test-replay-001",
    )

    first_response = send_request(request)
    second_response = send_request(request)

    assert first_response["success"] is True
    assert second_response["success"] is False
    assert "Autenticação" in second_response["error"]
