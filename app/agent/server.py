
import logging
import socket

from app.agent.handlers import handle_request
from app.agent.protocol import (
    create_response,
    decode_message,
    encode_message,
)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

BUFFER_SIZE = 4096
MAX_REQUEST_SIZE = 1024 * 1024
CLIENT_TIMEOUT = 5.0

logger = logging.getLogger(__name__)


class AgentServer:
    """
    Servidor TCP do SysView Agent.

    Recebe requisições JSON, encaminha para
    os handlers e devolve as respostas.

    Por segurança, utiliza localhost por padrão.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
    ) -> None:
        self.host = host
        self.port = port

        self._server_socket: socket.socket | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            raise RuntimeError(
                "O SysView Agent já está em execução."
            )

        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        try:
            server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            server_socket.bind(
                (self.host, self.port)
            )

            server_socket.listen(5)

            self._server_socket = server_socket
            self._running = True

            logger.info(
                "SysView Agent iniciado em %s:%s",
                self.host,
                self.port,
            )

            print(
                f"SysView Agent iniciado em "
                f"{self.host}:{self.port}"
            )

            while self._running:
                try:
                    client_socket, address = (
                        server_socket.accept()
                    )

                except OSError:
                    if not self._running:
                        break
                    raise

                logger.info(
                    "Conexão recebida de %s:%s",
                    address[0],
                    address[1],
                )

                self._handle_client(client_socket)

        finally:
            self._running = False

            if self._server_socket is server_socket:
                self._server_socket = None

            try:
                server_socket.close()
            except OSError:
                pass

            logger.info("SysView Agent encerrado")

    def _receive_request(
        self,
        client_socket: socket.socket,
    ) -> bytes:
        """
        Recebe uma mensagem JSON completa.

        Suporta mensagens divididas em vários
        pacotes TCP e limita seu tamanho.
        """

        data = bytearray()

        while True:
            chunk = client_socket.recv(BUFFER_SIZE)

            if not chunk:
                if not data:
                    raise ConnectionError(
                        "Cliente encerrou a conexão "
                        "sem enviar uma requisição."
                    )
                break

            data.extend(chunk)

            if len(data) > MAX_REQUEST_SIZE:
                raise ValueError(
                    "A requisição ultrapassou "
                    "o tamanho máximo permitido."
                )

            if b"\n" in data:
                return bytes(data).split(b"\n", 1)[0]

        return bytes(data).split(b"\n", 1)[0]

    def _handle_client(
        self,
        client_socket: socket.socket,
    ) -> None:
        try:
            client_socket.settimeout(CLIENT_TIMEOUT)

            data = self._receive_request(
                client_socket
            )

            request = decode_message(data)

            if request.get("version") != 1:
                raise ValueError(
                    "Versão do protocolo não suportada."
                )

            if request.get("type") != "request":
                raise ValueError(
                    "Tipo de mensagem inválido."
                )

            request_id = request.get("request_id")

            if (
                not isinstance(request_id, str)
                or not request_id
            ):
                raise ValueError(
                    "Identificador da requisição inválido."
                )

            if not isinstance(
                request.get("action"),
                str,
            ):
                raise ValueError(
                    "Ação da requisição inválida."
                )

            if not isinstance(
                request.get("payload"),
                dict,
            ):
                raise ValueError(
                    "Payload da requisição inválido."
                )

            response = handle_request(request)

            client_socket.sendall(
                encode_message(response)
            )

        except ValueError as error:
            logger.warning(
                "Requisição inválida: %s",
                error,
            )

            response = create_response(
                request_id="unknown",
                success=False,
                error=str(error),
            )

            try:
                client_socket.sendall(
                    encode_message(response)
                )
            except OSError:
                pass

        except socket.timeout:
            logger.warning(
                "Tempo limite de comunicação excedido"
            )

        except ConnectionError as error:
            logger.warning(
                "Conexão encerrada: %s",
                error,
            )

        except OSError as error:
            logger.warning(
                "Falha de comunicação: %s",
                error,
            )

        except Exception:
            logger.exception(
                "Erro inesperado no SysView Agent"
            )

        finally:
            try:
                client_socket.close()
            except OSError:
                pass

    def stop(self) -> None:
        self._running = False

        server_socket = self._server_socket

        if server_socket is None:
            return

        self._server_socket = None

        try:
            server_socket.close()
        except OSError:
            pass


def run_agent() -> None:
    server = AgentServer()
    server.start()


if __name__ == "__main__":
    run_agent()
