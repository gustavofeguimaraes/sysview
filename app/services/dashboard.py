from collections import deque

from app.services.cpu import get_cpu_info
from app.services.memory import get_memory_info
from app.services.disk import get_disk_info


# Quantidade máxima de pontos mantidos no histórico.
HISTORY_SIZE = 60


# Histórico de utilização dos recursos.
cpu_history = deque(maxlen=HISTORY_SIZE)
memory_history = deque(maxlen=HISTORY_SIZE)
disk_history = deque(maxlen=HISTORY_SIZE)


def get_dashboard_snapshot() -> dict:
    """Coleta os dados atuais necessários para o Dashboard."""

    cpu = get_cpu_info()
    memory = get_memory_info()
    disk = get_disk_info()

    snapshot = {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
    }

    # Guarda os valores atuais no histórico.
    cpu_history.append(cpu["usage_percent"])
    memory_history.append(memory["usage_percent"])
    disk_history.append(disk["usage_percent"])

    return snapshot


def get_dashboard_history() -> dict:
    """Retorna o histórico dos recursos monitorados."""

    return {
        "cpu": list(cpu_history),
        "memory": list(memory_history),
        "disk": list(disk_history),
    }


def clear_dashboard_history() -> None:
    """Limpa o histórico do Dashboard."""

    cpu_history.clear()
    memory_history.clear()
    disk_history.clear()