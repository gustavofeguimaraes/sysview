import psutil


# Processos que o SysView deve tratar com mais cuidado.
# Isso não impede a visualização, apenas evita uma finalização
# acidental sem confirmação adicional.
CRITICAL_PROCESS_NAMES = {
    "system",
    "system idle process",
    "registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "winlogon.exe",
    "svchost.exe",
    "dwm.exe",
    "explorer.exe",
}


def is_critical_process(
    name: str | None,
) -> bool:
    """
    Verifica se um processo é considerado crítico
    pelo SysView.
    """

    if not name:
        return False

    return (
        name.strip().lower()
        in CRITICAL_PROCESS_NAMES
    )


def get_processes() -> list[dict]:
    """
    Retorna informações dos processos em execução.
    """

    processes = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "username",
            "memory_percent",
            "exe",
            "status",
            "num_threads",
            "create_time",
        ]
    ):
        try:
            cpu_percent = process.cpu_percent(
                interval=None
            )

            info = process.info

            name = info.get(
                "name"
            )

            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": name,
                    "username": info.get("username"),
                    "cpu_percent": round(
                        cpu_percent,
                        2,
                    ),
                    "memory_percent": round(
                        info.get(
                            "memory_percent"
                        )
                        or 0,
                        2,
                    ),
                    "exe": info.get("exe"),
                    "status": info.get("status"),
                    "num_threads": info.get(
                        "num_threads"
                    ),
                    "create_time": info.get(
                        "create_time"
                    ),
                    "critical": is_critical_process(
                        name
                    ),
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    # CPU primeiro.
    processes.sort(
        key=lambda process: (
            process.get(
                "cpu_percent",
                0,
            )
        ),
        reverse=True,
    )

    return processes


def get_process(
    pid: int,
) -> dict | None:
    """
    Retorna os detalhes de um processo específico.
    """

    try:

        process = psutil.Process(
            pid
        )

        with process.oneshot():

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
                cpu_percent = process.cpu_percent(
                    interval=None
                )

            except psutil.AccessDenied:
                cpu_percent = 0.0

            try:
                memory_percent = process.memory_percent()

            except psutil.AccessDenied:
                memory_percent = 0.0

            try:
                memory_info = process.memory_info()

                memory_rss_mb = round(
                    memory_info.rss
                    / (
                        1024 * 1024
                    ),
                    2,
                )

            except psutil.AccessDenied:
                memory_rss_mb = 0.0

            name = process.name()

            return {
                "pid": process.pid,
                "name": name,
                "username": username,
                "status": process.status(),
                "cpu_percent": round(
                    cpu_percent,
                    2,
                ),
                "memory_percent": round(
                    memory_percent,
                    2,
                ),
                "memory_rss_mb": memory_rss_mb,
                "num_threads": process.num_threads(),
                "exe": exe,
                "create_time": create_time,
                "critical": is_critical_process(
                    name
                ),
            }

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return None


def terminate_process(
    pid: int,
) -> bool:
    """
    Solicita o encerramento de um processo.

    O Windows pode impedir a operação caso o processo
    seja protegido ou pertença a outro nível de privilégio.
    """

    try:

        process = psutil.Process(
            pid
        )

        process.terminate()

        return True

    except (
        psutil.NoSuchProcess,
        psutil.ZombieProcess,
    ):
        return False

    except psutil.AccessDenied as error:

        raise PermissionError(
            "Acesso negado pelo Windows "
            "para finalizar este processo."
        ) from error


def kill_process(
    pid: int,
) -> bool:
    """
    Força o encerramento de um processo.

    Mantida separada de terminate_process()
    para uso futuro.
    """

    try:

        process = psutil.Process(
            pid
        )

        process.kill()

        return True

    except (
        psutil.NoSuchProcess,
        psutil.ZombieProcess,
    ):
        return False

    except psutil.AccessDenied as error:

        raise PermissionError(
            "Acesso negado pelo Windows "
            "para finalizar este processo."
        ) from error