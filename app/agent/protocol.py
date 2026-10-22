import json


PROTOCOL_VERSION = 1


def create_request(
    action: str,
    request_id: str,
    payload: dict | None = None,
) -> dict:
    """
    Cria uma requisição no formato padrão do Agent.
    """

    if payload is None:
        payload = {}

    return {
        "version": PROTOCOL_VERSION,
        "type": "request",
        "request_id": request_id,
        "action": action,
        "payload": payload,
    }


def create_response(
    request_id: str,
    success: bool,
    payload: dict | None = None,
    error: str | None = None,
) -> dict:
    """
    Cria uma resposta no formato padrão do Agent.
    """

    if payload is None:
        payload = {}

    response = {
        "version": PROTOCOL_VERSION,
        "type": "response",
        "request_id": request_id,
        "success": success,
        "payload": payload,
    }

    if error is not None:
        response["error"] = error

    return response


def encode_message(message: dict) -> bytes:
    """
    Converte uma mensagem do protocolo para JSON em bytes.
    """

    return (
        json.dumps(
            message,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def decode_message(data: bytes) -> dict:
    """
    Converte JSON recebido em um dicionário.
    """

    try:
        message = json.loads(data.decode("utf-8"))
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ValueError(
            "Mensagem inválida."
        ) from exc

    if not isinstance(message, dict):
        raise ValueError(
            "A mensagem deve ser um objeto JSON."
        )

    return message