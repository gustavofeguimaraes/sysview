import socket

import psutil


def _get_process_info(pid: int | None) -> dict:
    if not pid:
        return {
            "process": None,
            "username": None,
            "exe": None,
            "create_time": None,
            "ppid": None,
        }

    try:
        process = psutil.Process(pid)

        try:
            name = process.name()
        except psutil.AccessDenied:
            name = "Acesso negado"

        try:
            username = process.username()
        except psutil.AccessDenied:
            username = "Acesso negado"

        try:
            exe = process.exe()
        except psutil.AccessDenied:
            exe = "Acesso negado"

        try:
            create_time = process.create_time()
        except psutil.AccessDenied:
            create_time = None

        try:
            ppid = process.ppid()
        except psutil.AccessDenied:
            ppid = None

        return {
            "process": name,
            "username": username,
            "exe": exe,
            "create_time": create_time,
            "ppid": ppid,
        }

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return {
            "process": None,
            "username": None,
            "exe": None,
            "create_time": None,
            "ppid": None,
        }


def _format_address(address):
    if not address:
        return None, None

    try:
        if isinstance(address, tuple):
            return address[0], address[1]

        return str(address), None

    except (IndexError, TypeError):
        return str(address), None


def _get_protocol(connection) -> str:
    if connection.type == socket.SOCK_STREAM:
        return "TCP"

    if connection.type == socket.SOCK_DGRAM:
        return "UDP"

    return str(connection.type)


def get_network_connections() -> list[dict]:
    """
    Retorna conexões TCP e UDP do computador.

    Inclui:
    - protocolo
    - endereço local
    - porta local
    - endereço remoto
    - porta remota
    - estado
    - PID
    - processo
    - usuário
    - executável
    - PPID
    - horário de criação
    """

    connections = []

    try:
        system_connections = psutil.net_connections(
            kind="inet"
        )

    except psutil.AccessDenied as error:
        raise PermissionError(
            "O Windows bloqueou o acesso às conexões de rede."
        ) from error

    for connection in system_connections:

        protocol = _get_protocol(connection)

        local_host, local_port = _format_address(
            connection.laddr
        )

        remote_host, remote_port = _format_address(
            connection.raddr
        )

        if local_host is None:
            local_host = "*"

        if local_port is None:
            local_port = "*"

        if remote_host is None:
            remote_host = "*"

        if remote_port is None:
            remote_port = "*"

        pid = connection.pid

        process_info = _get_process_info(pid)

        status = connection.status or "NONE"

        connections.append(
            {
                "protocol": protocol,
                "local_address": local_host,
                "local_port": local_port,
                "remote_address": remote_host,
                "remote_port": remote_port,
                "status": status,
                "pid": pid,
                "process": process_info["process"],
                "username": process_info["username"],
                "exe": process_info["exe"],
                "create_time": process_info["create_time"],
                "ppid": process_info["ppid"],
            }
        )

    connections.sort(
        key=lambda connection: (
            connection["protocol"],
            str(connection["local_address"]),
            str(connection["local_port"]),
            str(connection["process"]),
        )
    )

    return connections


def get_tcp_connections() -> list[dict]:
    return [
        connection
        for connection in get_network_connections()
        if connection["protocol"] == "TCP"
    ]


def get_udp_connections() -> list[dict]:
    return [
        connection
        for connection in get_network_connections()
        if connection["protocol"] == "UDP"
    ]


def get_listening_connections() -> list[dict]:
    return [
        connection
        for connection in get_network_connections()
        if connection["status"] == "LISTEN"
    ]


def get_established_connections() -> list[dict]:
    return [
        connection
        for connection in get_network_connections()
        if connection["status"] == "ESTABLISHED"
    ]


def get_connection_summary() -> dict:
    connections = get_network_connections()

    tcp = 0
    udp = 0
    listening = 0
    established = 0

    for connection in connections:

        if connection["protocol"] == "TCP":
            tcp += 1

        elif connection["protocol"] == "UDP":
            udp += 1

        if connection["status"] == "LISTEN":
            listening += 1

        if connection["status"] == "ESTABLISHED":
            established += 1

    return {
        "total": len(connections),
        "tcp": tcp,
        "udp": udp,
        "listening": listening,
        "established": established,
    }