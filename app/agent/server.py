import socket

from app.agent.handlers import handle_request
from app.agent.protocol import decode_message, encode_message

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
BUFFER_SIZE = 4096


class AgentServer:
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
        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

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

        print(
            f"SysView Agent iniciado em "
            f"{self.host}:{self.port}"
        )

        try:
            while self._running:
                try:
                    client_socket, address = (
                        server_socket.accept()
                    )
                except OSError:
                    if not self._running:
                        break

                    raise

                print(
                    f"Conexão recebida de "
                    f"{address[0]}:{address[1]}"
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

    def _handle_client(
        self,
        client_socket: socket.socket,
    ) -> None:
        try:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                return

            request = decode_message(data)

            response = handle_request(request)

            client_socket.sendall(
                encode_message(response)
            )

        except ValueError as exc:
            response = {
                "version": 1,
                "type": "response",
                "request_id": "unknown",
                "success": False,
                "payload": {},
                "error": str(exc),
            }

            try:
                client_socket.sendall(
                    encode_message(response)
                )
            except OSError:
                pass

        except OSError:
            pass

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