import socket
import time

import psutil


_previous_traffic = None
_previous_time = None


def get_network_info() -> list[dict]:
    """
    Retorna informações das interfaces de rede.
    """

    interfaces = []

    addresses = psutil.net_if_addrs()

    stats = psutil.net_if_stats()

    for interface_name, address_list in addresses.items():

        interface_stats = stats.get(
            interface_name
        )

        interface = {
            "name": interface_name,
            "is_up": (
                interface_stats.isup
                if interface_stats
                else False
            ),
            "speed_mbps": (
                interface_stats.speed
                if interface_stats
                else 0
            ),
            "mtu": (
                interface_stats.mtu
                if interface_stats
                else 0
            ),
            "ipv4": [],
            "ipv6": [],
            "mac": None,
        }

        for address in address_list:

            if address.family == psutil.AF_LINK:

                interface["mac"] = (
                    address.address
                )

            elif address.family == socket.AF_INET:

                interface["ipv4"].append(
                    address.address
                )

            elif address.family == socket.AF_INET6:

                interface["ipv6"].append(
                    address.address
                )

        interfaces.append(
            interface
        )

    return interfaces


def get_network_traffic() -> dict:
    """
    Retorna o tráfego acumulado de cada interface.
    """

    counters = psutil.net_io_counters(
        pernic=True
    )

    traffic = {}

    for interface_name, counter in counters.items():

        traffic[interface_name] = {
            "bytes_sent": counter.bytes_sent,
            "bytes_received": counter.bytes_recv,
            "packets_sent": counter.packets_sent,
            "packets_received": counter.packets_recv,
            "errors_in": counter.errin,
            "errors_out": counter.errout,
            "drops_in": counter.dropin,
            "drops_out": counter.dropout,
        }

    return traffic


def get_network_speed() -> dict:
    """
    Calcula a velocidade atual de upload e download
    de cada interface.
    """

    global _previous_traffic
    global _previous_time

    current_traffic = psutil.net_io_counters(
        pernic=True
    )

    current_time = time.monotonic()

    speeds = {}

    if (
        _previous_traffic is None
        or _previous_time is None
    ):

        for interface_name in current_traffic:

            speeds[interface_name] = {
                "upload_bps": 0.0,
                "download_bps": 0.0,
            }

    else:

        elapsed = (
            current_time
            - _previous_time
        )

        if elapsed <= 0:
            elapsed = 1

        for (
            interface_name,
            counter,
        ) in current_traffic.items():

            previous = (
                _previous_traffic.get(
                    interface_name
                )
            )

            if previous is None:

                speeds[interface_name] = {
                    "upload_bps": 0.0,
                    "download_bps": 0.0,
                }

                continue

            upload_bytes = max(
                0,
                (
                    counter.bytes_sent
                    - previous.bytes_sent
                ),
            )

            download_bytes = max(
                0,
                (
                    counter.bytes_recv
                    - previous.bytes_recv
                ),
            )

            speeds[interface_name] = {
                "upload_bps": (
                    upload_bytes
                    / elapsed
                ),
                "download_bps": (
                    download_bytes
                    / elapsed
                ),
            }

    _previous_traffic = (
        current_traffic
    )

    _previous_time = (
        current_time
    )

    return speeds


def get_network_connections() -> list[dict]:
    """
    Retorna conexões TCP e UDP observadas pelo sistema.

    Algumas conexões podem não apresentar PID ou nome do processo
    dependendo das permissões do Windows.
    """

    connections = []

    try:

        raw_connections = psutil.net_connections(
            kind="inet"
        )

    except (
        psutil.AccessDenied,
        PermissionError,
    ):

        return []

    for connection in raw_connections:

        try:

            family = (
                "IPv4"
                if connection.family
                == socket.AF_INET
                else "IPv6"
                if connection.family
                == socket.AF_INET6
                else str(
                    connection.family
                )
            )

            connection_type = (
                "TCP"
                if connection.type
                == socket.SOCK_STREAM
                else "UDP"
                if connection.type
                == socket.SOCK_DGRAM
                else str(
                    connection.type
                )
            )

            local_address = ""

            local_port = None

            if connection.laddr:

                local_address = (
                    connection.laddr.ip
                )

                local_port = (
                    connection.laddr.port
                )

            remote_address = ""

            remote_port = None

            if connection.raddr:

                remote_address = (
                    connection.raddr.ip
                )

                remote_port = (
                    connection.raddr.port
                )

            pid = connection.pid

            process_name = None

            if pid:

                try:

                    process_name = (
                        psutil.Process(
                            pid
                        ).name()
                    )

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):

                    process_name = None

            status = (
                connection.status
                if connection_type == "TCP"
                else "SEM_ESTADO"
            )

            connections.append(
                {
                    "type": connection_type,
                    "family": family,
                    "local_address": (
                        local_address
                        or "-"
                    ),
                    "local_port": (
                        local_port
                        or 0
                    ),
                    "remote_address": (
                        remote_address
                        or "-"
                    ),
                    "remote_port": (
                        remote_port
                        or 0
                    ),
                    "status": status,
                    "pid": pid or 0,
                    "process_name": (
                        process_name
                        or "-"
                    ),
                }
            )

        except Exception:
            continue

    connections.sort(
        key=lambda connection: (
            connection["type"],
            connection["local_port"],
            connection["remote_address"],
        )
    )

    return connections


def get_tcp_connections() -> list[dict]:
    """
    Retorna somente conexões TCP.
    """

    return [
        connection
        for connection
        in get_network_connections()
        if connection["type"] == "TCP"
    ]


def get_udp_connections() -> list[dict]:
    """
    Retorna somente conexões UDP.
    """

    return [
        connection
        for connection
        in get_network_connections()
        if connection["type"] == "UDP"
    ]


def format_bytes_per_second(
    value: float,
) -> str:
    """
    Converte bytes por segundo para formato legível.
    """

    if value < 1024:

        return f"{value:.0f} B/s"

    value /= 1024

    if value < 1024:

        return f"{value:.2f} KB/s"

    value /= 1024

    if value < 1024:

        return f"{value:.2f} MB/s"

    value /= 1024

    return f"{value:.2f} GB/s"


def get_network_snapshot() -> dict:
    """
    Retorna um snapshot completo da rede.
    """

    return {
        "interfaces": get_network_info(),
        "traffic": get_network_traffic(),
        "speed": get_network_speed(),
        "connections": get_network_connections(),
    }