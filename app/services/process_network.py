import psutil

from app.services.network_connections import (
    get_network_connections,
)


def get_process_network_connections(
    pid: int,
) -> list[dict]:
    """
    Retorna as conexões de rede pertencentes
    a um determinado processo.
    """

    connections = get_network_connections()

    return [
        connection
        for connection in connections
        if connection.get("pid") == pid
    ]


def get_network_connections_by_process() -> dict[int, list[dict]]:
    """
    Agrupa todas as conexões pelo PID do processo.
    """

    connections = get_network_connections()

    grouped: dict[int, list[dict]] = {}

    for connection in connections:
        pid = connection.get("pid")

        if not pid:
            continue

        if pid not in grouped:
            grouped[pid] = []

        grouped[pid].append(connection)

    return grouped


def get_process_network_summary(
    pid: int,
) -> dict | None:
    """
    Retorna um resumo de rede de um processo.
    """

    try:
        process = psutil.Process(pid)

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return None

    try:
        process_name = process.name()
    except psutil.AccessDenied:
        process_name = "Acesso negado"

    try:
        username = process.username()
    except psutil.AccessDenied:
        username = "Acesso negado"

    try:
        exe = process.exe()
    except psutil.AccessDenied:
        exe = "Acesso negado"

    connections = get_process_network_connections(pid)

    tcp = 0
    udp = 0
    listening = 0
    established = 0

    local_ports = set()
    remote_addresses = set()

    for connection in connections:
        protocol = connection.get("protocol")
        status = connection.get("status")

        if protocol == "TCP":
            tcp += 1

        elif protocol == "UDP":
            udp += 1

        if status == "LISTEN":
            listening += 1

        if status == "ESTABLISHED":
            established += 1

        local_port = connection.get("local_port")

        if local_port not in (None, "*"):
            local_ports.add(local_port)

        remote_address = connection.get(
            "remote_address"
        )

        if remote_address not in (None, "*"):
            remote_addresses.add(remote_address)

    return {
        "pid": pid,
        "process": process_name,
        "username": username,
        "exe": exe,
        "total_connections": len(connections),
        "tcp_connections": tcp,
        "udp_connections": udp,
        "listening": listening,
        "established": established,
        "local_ports": sorted(
            local_ports,
            key=str,
        ),
        "remote_addresses": sorted(
            remote_addresses
        ),
        "connections": connections,
    }


def get_processes_with_network() -> list[dict]:
    """
    Retorna processos que possuem
    pelo menos uma conexão de rede.
    """

    grouped = get_network_connections_by_process()

    processes = []

    for pid, connections in grouped.items():

        try:
            process = psutil.Process(pid)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

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

        tcp = sum(
            1
            for connection in connections
            if connection.get("protocol") == "TCP"
        )

        udp = sum(
            1
            for connection in connections
            if connection.get("protocol") == "UDP"
        )

        established = sum(
            1
            for connection in connections
            if connection.get("status") == "ESTABLISHED"
        )

        listening = sum(
            1
            for connection in connections
            if connection.get("status") == "LISTEN"
        )

        processes.append(
            {
                "pid": pid,
                "process": name,
                "username": username,
                "exe": exe,
                "connections": len(connections),
                "tcp": tcp,
                "udp": udp,
                "established": established,
                "listening": listening,
            }
        )

    processes.sort(
        key=lambda item: (
            item["connections"],
            item["process"] or "",
        ),
        reverse=True,
    )

    return processes