import json
import socket

from app.agent.protocol import (
    create_request,
    decode_message,
    encode_message,
)


class RemoteTransport:
    """
    Responsável somente pela comunicação TCP
    com o SysView Agent.

    Não conhece regras de negócio.
    """

    def __init__(
        self,
        host: str,
        port: int = 8765,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_request(
        self,
        action: str,
        request_id: str,
        payload: dict | None = None,
    ) -> dict:
        request = create_request(
            action=action,
            request_id=request_id,
            payload=payload,
        )

        with socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout,
        ) as client:
            client.sendall(
                encode_message(request)
            )

            data = bytearray()

            while True:
                chunk = client.recv(4096)

                if not chunk:
                    break

                data.extend(chunk)

                if b"\n" in chunk:
                    break

                try:
                    json.loads(
                        bytes(data).decode("utf-8")
                    )
                    break
                except (
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                ):
                    continue

        message_data = bytes(data).split(
            b"\n",
            1,
        )[0]

        response = decode_message(message_data)

        if response.get("request_id") != request_id:
            raise RuntimeError(
                "A resposta recebida não corresponde "
                "à requisição enviada."
            )

        if not response.get("success", False):
            error = response.get(
                "error",
                "O Agent retornou um erro.",
            )

            raise RuntimeError(error)

        return response