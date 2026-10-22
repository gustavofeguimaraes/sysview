
import json
import logging
import socket
import time

from app.agent.auth import (
    create_nonce,
    get_agent_secret,
    sign_request,
)
from app.agent.protocol import (
    create_request,
    decode_message,
    encode_message,
)


logger = logging.getLogger(__name__)


class RemoteTransport:
    """
    Comunicação TCP autenticada com o SysView Agent.

    Responsabilidades:
    - Abrir conexão com o Agent.
    - Criar e assinar requisições com HMAC-SHA256.
    - Enviar requisições.
    - Receber respostas.
    - Validar o identificador da requisição.
    - Tratar erros de comunicação.

    Não executa regras de negócio.

    Segurança:
    - A chave secreta nunca é enviada ao Agent.
    - Cada requisição possui timestamp e nonce únicos.
    - O servidor verifica a assinatura e rejeita repetições.
    - O transporte ainda não utiliza TLS.
    """

    DEFAULT_PORT = 8765
    DEFAULT_TIMEOUT = 5.0
    MAX_RESPONSE_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:

        if not isinstance(host, str) or not host.strip():
            raise ValueError(
                "Informe um endereço válido para o Agent."
            )

        if not isinstance(port, int) or not 1 <= port <= 65535:
            raise ValueError(
                "A porta deve estar entre 1 e 65535."
            )

        if timeout <= 0:
            raise ValueError(
                "O timeout deve ser maior que zero."
            )

        self.host = host.strip()
        self.port = port
        self.timeout = float(timeout)

    def _receive_response(
        self,
        client: socket.socket,
    ) -> bytes:
        """
        Recebe uma resposta JSON.

        Mantém compatibilidade com respostas
        terminadas por quebra de linha ou EOF.

        Limita o tamanho máximo da resposta.
        """

        data = bytearray()

        while True:
            chunk = client.recv(4096)

            if not chunk:
                if not data:
                    raise ConnectionError(
                        "O Agent encerrou a conexão "
                        "sem enviar uma resposta."
                    )
                break

            data.extend(chunk)

            if len(data) > self.MAX_RESPONSE_SIZE:
                raise ValueError(
                    "A resposta do Agent ultrapassou "
                    "o tamanho máximo permitido."
                )

            if b"\n" in data:
                return bytes(data).split(b"\n", 1)[0]

            try:
                json.loads(data.decode("utf-8"))
                return bytes(data)

            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
            ):
                continue

        return bytes(data).split(b"\n", 1)[0]

    def send_request(
        self,
        action: str,
        request_id: str,
        payload: dict | None = None,
    ) -> dict:
        """
        Envia uma requisição autenticada ao Agent.

        A requisição recebe:
        - timestamp: horário de criação;
        - nonce: identificador aleatório único;
        - signature: assinatura HMAC-SHA256.

        Retorna a resposta validada ou lança
        uma exceção em caso de falha.
        """

        if not isinstance(action, str) or not action.strip():
            raise ValueError(
                "A ação da requisição é inválida."
            )

        if (
            not isinstance(request_id, str)
            or not request_id.strip()
        ):
            raise ValueError(
                "O identificador da requisição é inválido."
            )

        if payload is not None and not isinstance(payload, dict):
            raise ValueError(
                "O payload deve ser um dicionário."
            )

        # Cria a requisição no formato padrão do protocolo.
        request = create_request(
            action=action,
            request_id=request_id,
            payload=payload,
        )

        # Adiciona os campos de autenticação.
        request["timestamp"] = int(time.time())
        request["nonce"] = create_nonce()

        # Assina a requisição usando a chave compartilhada.
        # A chave nunca é enviada pela rede.
        request["signature"] = sign_request(
            request,
            get_agent_secret(),
        )

        logger.debug(
            "Enviando ação %s ao Agent %s:%s",
            action,
            self.host,
            self.port,
        )

        try:
            with socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout,
            ) as client:

                

                client.sendall(
                    encode_message(request)
                )

                message_data = self._receive_response(
                    client
                )

        except socket.timeout as error:
            raise TimeoutError(
                f"O Agent {self.host}:{self.port} "
                "não respondeu dentro do tempo limite."
            ) from error

        except ConnectionRefusedError as error:
            raise ConnectionError(
                f"Conexão recusada por "
                f"{self.host}:{self.port}. "
                "Verifique se o SysView Agent "
                "está em execução."
            ) from error

        except OSError as error:
            raise ConnectionError(
                f"Falha na comunicação com "
                f"{self.host}:{self.port}: {error}"
            ) from error

        try:
            response = decode_message(message_data)

        except (
            ValueError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as error:
            raise ValueError(
                "O Agent retornou uma resposta inválida."
            ) from error

        if not isinstance(response, dict):
            raise ValueError(
                "A resposta do Agent deve ser um objeto."
            )

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

            raise RuntimeError(str(error))

        logger.debug(
            "Resposta recebida do Agent para ação %s",
            action,
        )

        return response
