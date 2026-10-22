import psutil

from app.services.windows_services import get_windows_services


def get_services_by_pid(pid: int) -> list[dict]:
    """
    Retorna os serviços do Windows associados a um determinado PID.
    """

    services = []

    for service in get_windows_services():
        service_pid = service.get("pid")

        if service_pid is None:
            continue

        try:
            if int(service_pid) != int(pid):
                continue
        except (TypeError, ValueError):
            continue

        services.append(service)

    return services


def get_process_service_summary(pid: int) -> dict | None:
    """
    Retorna um resumo dos serviços relacionados a um processo.
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

    services = get_services_by_pid(pid)

    running = 0
    stopped = 0
    other = 0

    for service in services:
        status = str(
            service.get("status") or ""
        ).lower()

        if status == "running":
            running += 1

        elif status == "stopped":
            stopped += 1

        else:
            other += 1

    return {
        "pid": pid,
        "process": process_name,
        "username": username,
        "exe": exe,
        "total_services": len(services),
        "running": running,
        "stopped": stopped,
        "other": other,
        "services": services,
    }


def get_processes_with_services() -> list[dict]:
    """
    Retorna processos que possuem pelo menos
    um serviço do Windows associado.
    """

    services = get_windows_services()

    services_by_pid: dict[int, list[dict]] = {}

    for service in services:
        pid = service.get("pid")

        if pid is None:
            continue

        try:
            pid = int(pid)
        except (TypeError, ValueError):
            continue

        if pid <= 0:
            continue

        if pid not in services_by_pid:
            services_by_pid[pid] = []

        services_by_pid[pid].append(service)

    processes = []

    for pid, process_services in services_by_pid.items():

        try:
            process = psutil.Process(pid)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

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

        running = sum(
            1
            for service in process_services
            if str(
                service.get("status") or ""
            ).lower()
            == "running"
        )

        stopped = sum(
            1
            for service in process_services
            if str(
                service.get("status") or ""
            ).lower()
            == "stopped"
        )

        processes.append(
            {
                "pid": pid,
                "process": process_name,
                "username": username,
                "exe": exe,
                "services": len(process_services),
                "running": running,
                "stopped": stopped,
                "service_list": process_services,
            }
        )

    processes.sort(
        key=lambda item: (
            item["services"],
            item["process"] or "",
        ),
        reverse=True,
    )

    return processes