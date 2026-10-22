import psutil

from app.services.network_connections import get_network_connections


def _safe_process_info(pid: int) -> dict | None:
    try:
        process = psutil.Process(pid)

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return None

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
        status = process.status()
    except psutil.AccessDenied:
        status = "Acesso negado"

    try:
        cpu_percent = process.cpu_percent(interval=None)
    except psutil.AccessDenied:
        cpu_percent = 0.0

    try:
        memory_percent = process.memory_percent()
    except psutil.AccessDenied:
        memory_percent = 0.0

    try:
        memory_rss_mb = (
            process.memory_info().rss
            / (1024 * 1024)
        )
    except psutil.AccessDenied:
        memory_rss_mb = 0.0

    try:
        num_threads = process.num_threads()
    except psutil.AccessDenied:
        num_threads = None

    try:
        create_time = process.create_time()
    except psutil.AccessDenied:
        create_time = None

    try:
        ppid = process.ppid()
    except psutil.AccessDenied:
        ppid = None

    return {
        "pid": pid,
        "name": name,
        "username": username,
        "exe": exe,
        "status": status,
        "cpu_percent": round(cpu_percent, 2),
        "memory_percent": round(memory_percent, 2),
        "memory_rss_mb": round(memory_rss_mb, 2),
        "num_threads": num_threads,
        "create_time": create_time,
        "ppid": ppid,
    }


def _get_process_connections(
    pid: int,
    connections: list[dict],
) -> list[dict]:
    return [
        connection
        for connection in connections
        if connection.get("pid") == pid
    ]


def _build_network_summary(
    connections: list[dict],
) -> dict:
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

        remote_address = connection.get("remote_address")

        if remote_address not in (None, "*"):
            remote_addresses.add(remote_address)

    return {
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
            remote_addresses,
            key=str,
        ),
    }


def get_service_process_network(
    service: dict,
    connections: list[dict] | None = None,
) -> dict:
    """
    Cria a correlação:

        Serviço → Processo → Rede

    Recebe um dicionário de serviço e utiliza o PID do serviço
    para localizar o processo correspondente e suas conexões.
    """

    if not service:
        return {
            "service": None,
            "process": None,
            "network": {
                "total_connections": 0,
                "tcp_connections": 0,
                "udp_connections": 0,
                "listening": 0,
                "established": 0,
                "local_ports": [],
                "remote_addresses": [],
            },
            "connections": [],
        }

    pid = service.get("pid")

    try:
        pid = int(pid) if pid is not None else None
    except (TypeError, ValueError):
        pid = None

    if pid is None or pid <= 0:
        return {
            "service": service,
            "process": None,
            "network": {
                "total_connections": 0,
                "tcp_connections": 0,
                "udp_connections": 0,
                "listening": 0,
                "established": 0,
                "local_ports": [],
                "remote_addresses": [],
            },
            "connections": [],
        }

    process = _safe_process_info(pid)

    if connections is None:
        connections = get_network_connections()

    process_connections = _get_process_connections(
        pid,
        connections,
    )

    network = _build_network_summary(
        process_connections
    )

    return {
        "service": service,
        "process": process,
        "network": network,
        "connections": process_connections,
    }


def get_service_process_network_by_pid(
    service_pid: int,
    connections: list[dict] | None = None,
) -> dict:
    """
    Versão simplificada quando temos somente o PID do serviço.
    """

    try:
        pid = int(service_pid)
    except (TypeError, ValueError):
        return {
            "process": None,
            "network": {
                "total_connections": 0,
                "tcp_connections": 0,
                "udp_connections": 0,
                "listening": 0,
                "established": 0,
                "local_ports": [],
                "remote_addresses": [],
            },
            "connections": [],
        }

    process = _safe_process_info(pid)

    if connections is None:
        connections = get_network_connections()

    process_connections = _get_process_connections(
        pid,
        connections,
    )

    network = _build_network_summary(
        process_connections
    )

    return {
        "process": process,
        "network": network,
        "connections": process_connections,
    }


def get_services_processes_network(
    services: list[dict],
    connections: list[dict] | None = None,
) -> list[dict]:
    """
    Cria a correlação para vários serviços.

    Estrutura:

        serviço
          ↓
        processo
          ↓
        rede
    """

    if connections is None:
        connections = get_network_connections()

    result = []

    for service in services:
        data = get_service_process_network(
            service,
            connections,
        )

        result.append(data)

    return result