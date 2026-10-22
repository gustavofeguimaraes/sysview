
import logging
import psutil

logger = logging.getLogger(__name__)

SERVICE_ERRORS = (
    psutil.NoSuchProcess,
    psutil.AccessDenied,
    psutil.ZombieProcess,
    PermissionError,
    FileNotFoundError,
    OSError,
)


def _read_service_field(service, field, default=None):
    """Consulta um atributo sem interromper a listagem."""
    try:
        return getattr(service, field)()
    except SERVICE_ERRORS as error:
        logger.debug(
            "Não foi possível consultar %s do serviço %s: %s",
            field,
            getattr(service, "_name", "desconhecido"),
            error,
        )
        return default


def get_windows_services() -> list[dict]:
    """Lista os serviços acessíveis do Windows."""

    services = []

    try:
        iterator = psutil.win_service_iter()

        for service in iterator:
            try:
                name = service.name()

                services.append({
                    "name": name,
                    "display_name": _read_service_field(
                        service, "display_name", name
                    ),
                    "status": _read_service_field(
                        service, "status", "unknown"
                    ),
                    "start_type": _read_service_field(
                        service, "start_type", "unknown"
                    ),
                    "pid": _read_service_field(
                        service, "pid"
                    ),
                    "username": _read_service_field(
                        service, "username"
                    ),
                    "binpath": _read_service_field(
                        service, "binpath"
                    ),
                    "description": _read_service_field(
                        service, "description"
                    ),
                })

            except SERVICE_ERRORS as error:
                logger.debug(
                    "Serviço ignorado por erro de acesso: %s",
                    error,
                )
                continue

    except SERVICE_ERRORS as error:
        logger.warning(
            "Não foi possível concluir a listagem de serviços: %s",
            error,
        )

    services.sort(
        key=lambda item: (
            item["display_name"] or ""
        ).lower()
    )

    return services


def get_service(service_name: str) -> dict | None:
    """Retorna informações de um serviço específico."""

    try:
        service = psutil.win_service_get(service_name)
        return service.as_dict()

    except SERVICE_ERRORS as error:
        logger.warning(
            "Falha ao consultar serviço %s: %s",
            service_name,
            error,
        )
        return None


def start_service(service_name: str) -> bool:
    """Inicia um serviço do Windows."""

    service = psutil.win_service_get(service_name)
    service.start()
    return True


def stop_service(service_name: str) -> bool:
    """Para um serviço do Windows."""

    service = psutil.win_service_get(service_name)
    service.stop()
    return True


def restart_service(service_name: str) -> bool:
    """Reinicia um serviço do Windows."""

    service = psutil.win_service_get(service_name)

    service.stop()
    service.wait(timeout=10)
    service.start()

    return True
