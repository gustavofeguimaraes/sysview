import psutil


def get_windows_services() -> list[dict]:
    """Retorna os serviços do Windows."""

    services = []

    for service in psutil.win_service_iter():

        try:
            name = service.name()

            try:
                display_name = service.display_name()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                display_name = name

            try:
                status = service.status()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                status = "unknown"

            try:
                start_type = service.start_type()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                start_type = "unknown"

            try:
                pid = service.pid()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                pid = None

            try:
                username = service.username()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                username = None

            try:
                binpath = service.binpath()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                binpath = None

            try:
                description = service.description()

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                FileNotFoundError,
            ):
                description = None

            services.append(
                {
                    "name": name,
                    "display_name": display_name,
                    "status": status,
                    "start_type": start_type,
                    "pid": pid,
                    "username": username,
                    "binpath": binpath,
                    "description": description,
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            FileNotFoundError,
        ):
            continue

    services.sort(
        key=lambda service: (
            service["display_name"] or ""
        ).lower()
    )

    return services


def get_service(
    service_name: str,
) -> dict | None:
    """Retorna um serviço específico."""

    try:
        service = psutil.win_service_get(
            service_name
        )

        return service.as_dict()

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
        FileNotFoundError,
    ):
        return None


def start_service(
    service_name: str,
) -> bool:
    """Inicia um serviço do Windows."""

    service = psutil.win_service_get(
        service_name
    )

    service.start()

    return True


def stop_service(
    service_name: str,
) -> bool:
    """Para um serviço do Windows."""

    service = psutil.win_service_get(
        service_name
    )

    service.stop()

    return True


def restart_service(
    service_name: str,
) -> bool:
    """Reinicia um serviço do Windows."""

    service = psutil.win_service_get(
        service_name
    )

    service.stop()

    service.wait(
        timeout=10
    )

    service.start()

    return True