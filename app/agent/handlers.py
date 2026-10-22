from app.agent.protocol import create_response
from app.services.cpu import get_cpu_info
from app.services.disk import get_disk_info
from app.services.memory import get_memory_info
from app.services.network import (
    get_network_info,
    get_network_speed,
    get_network_traffic,
)
from app.services.network_connections import get_network_connections
from app.services.processes import (
    get_process,
    get_processes,
)
from app.services.system_info import get_system_info
from app.services.windows_services import get_windows_services


SUPPORTED_ACTIONS = {
    "ping",
    "agent_info",
    "system_info",
    "cpu_info",
    "memory_info",
    "disk_info",
    "network_info",
    "network_connections",
    "processes",
    "process_info",
    "services",
}


def handle_request(request: dict) -> dict:
    request_id = request.get("request_id")

    if not request_id:
        return create_response(
            request_id="unknown",
            success=False,
            error="request_id não informado.",
        )

    if request.get("type") != "request":
        return create_response(
            request_id=request_id,
            success=False,
            error="Tipo de mensagem inválido.",
        )

    action = request.get("action")

    if action not in SUPPORTED_ACTIONS:
        return create_response(
            request_id=request_id,
            success=False,
            error=f"Ação não suportada: {action}",
        )

    if action == "ping":
        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "message": "pong",
            },
        )

    if action == "agent_info":
        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "name": "SysView Agent",
                "version": "0.1.0",
                "protocol_version": 1,
            },
        )

    if action == "system_info":
        return create_response(
            request_id=request_id,
            success=True,
            payload=get_system_info(),
        )

    if action == "cpu_info":
        return create_response(
            request_id=request_id,
            success=True,
            payload=get_cpu_info(),
        )

    if action == "memory_info":
        return create_response(
            request_id=request_id,
            success=True,
            payload=get_memory_info(),
        )

    if action == "disk_info":
        return create_response(
            request_id=request_id,
            success=True,
            payload=get_disk_info(),
        )

    if action == "network_info":
        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "interfaces": get_network_info(),
                "traffic": get_network_traffic(),
                "speed": get_network_speed(),
            },
        )

    if action == "network_connections":
        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "connections": get_network_connections(),
            },
        )

    if action == "processes":
        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "processes": get_processes(),
            },
        )

    if action == "process_info":
        payload = request.get("payload") or {}
        pid = payload.get("pid")

        if pid is None:
            return create_response(
                request_id=request_id,
                success=False,
                error="PID não informado.",
            )

        try:
            pid = int(pid)
        except (TypeError, ValueError):
            return create_response(
                request_id=request_id,
                success=False,
                error="PID inválido.",
            )

        try:
            process = get_process(pid)
        except Exception as error:
            return create_response(
                request_id=request_id,
                success=False,
                error=f"Erro ao consultar processo: {error}",
            )

        if process is None:
            return create_response(
                request_id=request_id,
                success=False,
                error=f"Processo não encontrado: {pid}",
            )

        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "process": process,
            },
        )

    if action == "services":
        return create_response(
            request_id=request_id,
            success=True,
            payload={
                "services": get_windows_services(),
            },
        )

    return create_response(
        request_id=request_id,
        success=False,
        error="Ação não implementada.",
    )