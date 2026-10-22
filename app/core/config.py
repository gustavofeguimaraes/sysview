from pathlib import Path


# ==============================================================
# DIRETÓRIOS
# ==============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "sysview.log"


# ==============================================================
# APLICAÇÃO
# ==============================================================

APP_NAME = "SysView"
APP_VERSION = "0.1.0"
ENVIRONMENT = "development"


# ==============================================================
# MONITORAMENTO
# ==============================================================

MONITOR_INTERVALS = {
    "dashboard": 1.0,
    "network": 1.0,
    "network_connections": 3.0,
    "process": 3.0,
    "process_network": 3.0,
    "process_services": 10.0,
    "services": 10.0,
    "system": 30.0,
}


# ==============================================================
# VALIDAÇÃO
# ==============================================================

REQUIRED_MONITOR_INTERVALS = {
    "dashboard",
    "network",
    "network_connections",
    "process",
    "process_network",
    "process_services",
    "services",
    "system",
}


def validate_monitor_intervals(
    intervals: dict | None = None,
) -> dict:
    """
    Valida os intervalos utilizados pelo monitor.

    Regras:
    - todas as configurações obrigatórias precisam existir;
    - os valores precisam ser números;
    - os valores precisam ser maiores que zero.

    Retorna uma cópia validada do dicionário.
    """

    if intervals is None:
        intervals = MONITOR_INTERVALS

    if not isinstance(intervals, dict):
        raise TypeError(
            "Os intervalos do monitor devem ser um dicionário."
        )

    missing = (
        REQUIRED_MONITOR_INTERVALS
        - set(intervals.keys())
    )

    if missing:
        missing_names = ", ".join(
            sorted(missing)
        )

        raise ValueError(
            "Intervalos obrigatórios ausentes: "
            f"{missing_names}"
        )

    validated = {}

    for name in REQUIRED_MONITOR_INTERVALS:
        value = intervals[name]

        if isinstance(value, bool):
            raise TypeError(
                f"O intervalo '{name}' deve ser numérico."
            )

        if not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                f"O intervalo '{name}' deve ser numérico."
            )

        if value <= 0:
            raise ValueError(
                f"O intervalo '{name}' "
                "deve ser maior que zero."
            )

        validated[name] = float(value)

    return validated


# Valida a configuração padrão durante
# a inicialização do módulo.
MONITOR_INTERVALS = validate_monitor_intervals(
    MONITOR_INTERVALS
)