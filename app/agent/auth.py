
import hashlib
import hmac
import json
import os
import secrets
import time


AUTH_WINDOW_SECONDS = 30


def get_agent_secret() -> str:
    """Obtém a chave de autenticação configurada no ambiente."""
    secret = os.getenv("SYSVIEW_AGENT_SECRET", "")

    if len(secret) < 32:
        raise RuntimeError(
            "Configure SYSVIEW_AGENT_SECRET com uma chave "
            "aleatória de pelo menos 32 caracteres."
        )

    return secret


def create_nonce() -> str:
    """Cria um identificador aleatório para cada requisição."""
    return secrets.token_hex(16)


def _canonical_message(request: dict) -> bytes:
    """Produz uma representação estável para assinatura."""
    fields = {
        "version": request.get("version"),
        "type": request.get("type"),
        "request_id": request.get("request_id"),
        "action": request.get("action"),
        "payload": request.get("payload"),
        "timestamp": request.get("timestamp"),
        "nonce": request.get("nonce"),
    }

    return json.dumps(
        fields,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sign_request(request: dict, secret: str) -> str:
    """Assina a requisição sem transmitir a chave secreta."""
    return hmac.new(
        secret.encode("utf-8"),
        _canonical_message(request),
        hashlib.sha256,
    ).hexdigest()


def authenticate_request(
    request: dict,
    secret: str,
    used_nonces: set[str],
) -> bool:
    """Verifica assinatura, validade temporal e repetição."""
    timestamp = request.get("timestamp")
    nonce = request.get("nonce")
    signature = request.get("signature")

    if (
        type(timestamp) is not int
        or not isinstance(nonce, str)
        or len(nonce) != 32
        or not isinstance(signature, str)
    ):
        return False

    if abs(time.time() - timestamp) > AUTH_WINDOW_SECONDS:
        return False

    if nonce in used_nonces:
        return False

    expected = sign_request(request, secret)

    if not hmac.compare_digest(expected, signature):
        return False

    used_nonces.add(nonce)
    return True
