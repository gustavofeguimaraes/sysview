from app.agent.handlers import handle_request


def test_ping():
    response = handle_request(
        {
            "version": 1,
            "type": "request",
            "request_id": "req-001",
            "action": "ping",
            "payload": {},
        }
    )

    assert response["success"] is True
    assert response["request_id"] == "req-001"
    assert response["payload"]["message"] == "pong"


def test_agent_info():
    response = handle_request(
        {
            "version": 1,
            "type": "request",
            "request_id": "req-002",
            "action": "agent_info",
            "payload": {},
        }
    )

    assert response["success"] is True
    assert response["payload"]["name"] == "SysView Agent"
    assert response["payload"]["version"] == "0.1.0"


def test_unsupported_action():
    response = handle_request(
        {
            "version": 1,
            "type": "request",
            "request_id": "req-003",
            "action": "shutdown",
            "payload": {},
        }
    )

    assert response["success"] is False
    assert "não suportada" in response["error"]


def test_invalid_message_type():
    response = handle_request(
        {
            "version": 1,
            "type": "response",
            "request_id": "req-004",
            "action": "ping",
            "payload": {},
        }
    )

    assert response["success"] is False


def test_missing_request_id():
    response = handle_request(
        {
            "version": 1,
            "type": "request",
            "action": "ping",
            "payload": {},
        }
    )

    assert response["success"] is False