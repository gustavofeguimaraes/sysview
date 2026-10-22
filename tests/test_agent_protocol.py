import pytest

from app.agent.protocol import (
    PROTOCOL_VERSION,
    create_request,
    create_response,
    decode_message,
    encode_message,
)


def test_create_request():
    request = create_request(
        action="ping",
        request_id="req-001",
    )

    assert request["version"] == PROTOCOL_VERSION
    assert request["type"] == "request"
    assert request["request_id"] == "req-001"
    assert request["action"] == "ping"
    assert request["payload"] == {}


def test_create_request_with_payload():
    request = create_request(
        action="test",
        request_id="req-002",
        payload={"value": 123},
    )

    assert request["payload"] == {
        "value": 123,
    }


def test_create_response_success():
    response = create_response(
        request_id="req-001",
        success=True,
        payload={"message": "pong"},
    )

    assert response["type"] == "response"
    assert response["request_id"] == "req-001"
    assert response["success"] is True
    assert response["payload"]["message"] == "pong"
    assert "error" not in response


def test_create_response_error():
    response = create_response(
        request_id="req-002",
        success=False,
        error="Erro de teste.",
    )

    assert response["success"] is False
    assert response["error"] == "Erro de teste."


def test_encode_and_decode_message():
    original = create_request(
        action="ping",
        request_id="req-003",
    )

    encoded = encode_message(original)
    decoded = decode_message(encoded)

    assert decoded == original


def test_decode_invalid_json():
    with pytest.raises(ValueError):
        decode_message(b"mensagem invalida")


def test_decode_requires_object():
    with pytest.raises(ValueError):
        decode_message(b"[]")