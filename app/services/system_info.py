
import getpass
import platform
import socket
import time

import psutil


def bytes_to_gb(value: int) -> float:
    """Converte bytes para GB."""

    return round(
        value / (1024 ** 3),
        2,
    )


def format_uptime(seconds: float) -> str:
    """Converte segundos de uptime para formato legível."""

    seconds = int(seconds)

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    parts = []

    if days:
        parts.append(
            f"{days}d"
        )

    if hours:
        parts.append(
            f"{hours}h"
        )

    if minutes:
        parts.append(
            f"{minutes}min"
        )

    if not parts:
        parts.append(
            f"{seconds}s"
        )

    return " ".join(parts)


def get_gpu_info() -> list[dict]:
    """
    Tenta obter informações das GPUs no Windows.

    A consulta utiliza WMI através do PowerShell.
    Se não estiver disponível, retorna uma lista vazia.
    """

    if platform.system() != "Windows":
        return []

    try:
        import json
        import subprocess

        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-CimInstance Win32_VideoController | "
                "Select-Object Name,AdapterRAM,DriverVersion,"
                "VideoProcessor,CurrentHorizontalResolution,"
                "CurrentVerticalResolution,CurrentRefreshRate | "
                "ConvertTo-Json -Compress"
            ),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if hasattr(
                    subprocess,
                    "CREATE_NO_WINDOW",
                )
                else 0
            ),
        )

        if result.returncode != 0:
            return []

        output = result.stdout.strip()

        if not output:
            return []

        data = json.loads(output)

        if isinstance(data, dict):
            data = [data]

        gpus = []

        for gpu in data:
            adapter_ram = gpu.get(
                "AdapterRAM"
            )

            gpus.append(
                {
                    "name": (
                        gpu.get("Name")
                        or "Desconhecida"
                    ),
                    "memory_gb": (
                        round(
                            adapter_ram
                            / (1024 ** 3),
                            2,
                        )
                        if adapter_ram
                        else None
                    ),
                    "driver_version": (
                        gpu.get(
                            "DriverVersion"
                        )
                        or "-"
                    ),
                    "video_processor": (
                        gpu.get(
                            "VideoProcessor"
                        )
                        or "-"
                    ),
                    "resolution": (
                        (
                            f"{gpu.get('CurrentHorizontalResolution')}x"
                            f"{gpu.get('CurrentVerticalResolution')}"
                        )
                        if gpu.get(
                            "CurrentHorizontalResolution"
                        )
                        and gpu.get(
                            "CurrentVerticalResolution"
                        )
                        else "-"
                    ),
                    "refresh_rate": (
                        gpu.get(
                            "CurrentRefreshRate"
                        )
                        or "-"
                    ),
                }
            )

        return gpus

    except (
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
        OSError,
        Exception,
    ):
        return []


def get_disk_partitions() -> list[dict]:
    """
    Retorna as partições/discos disponíveis no sistema.
    """

    partitions = []

    for partition in psutil.disk_partitions(
        all=False
    ):
        try:
            usage = psutil.disk_usage(
                partition.mountpoint
            )

            partitions.append(
                {
                    "device": (
                        partition.device
                    ),
                    "mountpoint": (
                        partition.mountpoint
                    ),
                    "filesystem": (
                        partition.fstype
                        or "-"
                    ),
                    "total_gb": bytes_to_gb(
                        usage.total
                    ),
                    "used_gb": bytes_to_gb(
                        usage.used
                    ),
                    "free_gb": bytes_to_gb(
                        usage.free
                    ),
                    "usage_percent": (
                        usage.percent
                    ),
                }
            )

        except (
            PermissionError,
            OSError,
        ):
            continue

    return partitions


def get_network_adapters() -> list[dict]:
    """
    Retorna informações dos adaptadores de rede.
    """

    adapters = []

    addresses = (
        psutil.net_if_addrs()
    )

    stats = (
        psutil.net_if_stats()
    )

    for interface_name, address_list in (
        addresses.items()
    ):
        interface_stats = stats.get(
            interface_name
        )

        adapter = {
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
            "ipv4": [],
            "ipv6": [],
            "mac": None,
        }

        for address in address_list:

            if address.family == psutil.AF_LINK:
                adapter["mac"] = (
                    address.address
                )

            elif address.family == socket.AF_INET:
                adapter["ipv4"].append(
                    address.address
                )

            elif address.family == socket.AF_INET6:
                adapter["ipv6"].append(
                    address.address
                )

        adapters.append(
            adapter
        )

    return adapters


def get_system_info() -> dict:
    """
    Retorna informações completas do computador.

    A função reúne informações de hardware,
    sistema, armazenamento e rede.
    """

    # =========================================================
    # SISTEMA OPERACIONAL
    # =========================================================

    operating_system = (
        platform.system()
    )

    operating_system_version = (
        platform.version()
    )

    operating_system_release = (
        platform.release()
    )

    architecture = (
        platform.machine()
    )

    processor = (
        platform.processor()
    )

    python_version = (
        platform.python_version()
    )

    platform_name = (
        platform.platform()
    )

    # =========================================================
    # IDENTIFICAÇÃO
    # =========================================================

    hostname = (
        socket.gethostname()
    )

    try:
        current_user = (
            getpass.getuser()
        )

    except Exception:
        current_user = (
            "Desconhecido"
        )

    # =========================================================
    # CPU
    # =========================================================

    physical_cores = (
        psutil.cpu_count(
            logical=False
        )
    )

    logical_cores = (
        psutil.cpu_count(
            logical=True
        )
    )

    cpu_frequency = (
        psutil.cpu_freq()
    )

    frequency_mhz = (
        round(
            cpu_frequency.current,
            2,
        )
        if cpu_frequency
        else None
    )

    cpu_usage_percent = (
        psutil.cpu_percent(
            interval=None
        )
    )

    # =========================================================
    # MEMÓRIA
    # =========================================================

    memory = (
        psutil.virtual_memory()
    )

    # =========================================================
    # DISCO PRINCIPAL
    # =========================================================

    disk = psutil.disk_usage(
        "/"
    )

    # =========================================================
    # UPTIME
    # =========================================================

    boot_timestamp = (
        psutil.boot_time()
    )

    current_timestamp = (
        time.time()
    )

    uptime_seconds = max(
        0,
        current_timestamp
        - boot_timestamp,
    )

    boot_datetime = (
        time.strftime(
            "%d/%m/%Y %H:%M:%S",
            time.localtime(
                boot_timestamp
            ),
        )
    )

    # =========================================================
    # HARDWARE EXTRA
    # =========================================================

    gpus = get_gpu_info()

    partitions = (
        get_disk_partitions()
    )

    network_adapters = (
        get_network_adapters()
    )

    # =========================================================
    # RESULTADO
    # =========================================================

    return {
        # -----------------------------------------------------
        # Identificação
        # -----------------------------------------------------

        "hostname": hostname,

        "current_user": (
            current_user
        ),

        # -----------------------------------------------------
        # Sistema operacional
        # -----------------------------------------------------

        "operating_system": (
            operating_system
        ),

        "operating_system_version": (
            operating_system_version
        ),

        "operating_system_release": (
            operating_system_release
        ),

        "architecture": architecture,

        "platform": platform_name,

        # -----------------------------------------------------
        # Python
        # -----------------------------------------------------

        "python_version": (
            python_version
        ),

        # -----------------------------------------------------
        # CPU
        # -----------------------------------------------------

        "processor": processor,

        "physical_cores": (
            physical_cores
        ),

        "logical_cores": (
            logical_cores
        ),

        "cpu_count": (
            logical_cores
        ),

        "frequency_mhz": (
            frequency_mhz
        ),

        "cpu_usage_percent": (
            cpu_usage_percent
        ),

        # -----------------------------------------------------
        # Memória
        # -----------------------------------------------------

        "memory_total_gb": (
            bytes_to_gb(
                memory.total
            )
        ),

        "memory_available_gb": (
            bytes_to_gb(
                memory.available
            )
        ),

        "memory_used_gb": (
            bytes_to_gb(
                memory.used
            )
        ),

        "memory_usage_percent": (
            memory.percent
        ),

        # -----------------------------------------------------
        # Disco principal
        # -----------------------------------------------------

        "disk_total_gb": (
            bytes_to_gb(
                disk.total
            )
        ),

        "disk_used_gb": (
            bytes_to_gb(
                disk.used
            )
        ),

        "disk_free_gb": (
            bytes_to_gb(
                disk.free
            )
        ),

        "disk_usage_percent": (
            disk.percent
        ),

        # -----------------------------------------------------
        # Armazenamento
        # -----------------------------------------------------

        "partitions": partitions,

        # -----------------------------------------------------
        # GPU
        # -----------------------------------------------------

        "gpus": gpus,

        # -----------------------------------------------------
        # Rede
        # -----------------------------------------------------

        "network_adapters": (
            network_adapters
        ),

        # -----------------------------------------------------
        # Uptime
        # -----------------------------------------------------

        "boot_time": (
            boot_datetime
        ),

        "uptime_seconds": (
            uptime_seconds
        ),

        "uptime": (
            format_uptime(
                uptime_seconds
            )
        ),
    }

