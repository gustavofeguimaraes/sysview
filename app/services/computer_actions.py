import ctypes
import platform
import subprocess


def _check_windows() -> None:
    """Verifica se o sistema atual é Windows."""

    if platform.system() != "Windows":
        raise RuntimeError(
            "Esta ação está disponível somente no Windows."
        )


def _run_shutdown_command(
    arguments: list[str],
) -> None:
    """Executa um comando do Windows relacionado a desligamento."""

    _check_windows()

    result = subprocess.run(
        [
            "shutdown",
            *arguments,
        ],
        capture_output=True,
        text=True,
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
        error = (
            result.stderr.strip()
            or result.stdout.strip()
            or "O Windows não conseguiu executar a ação."
        )

        raise RuntimeError(error)


def lock_workstation() -> None:
    """Bloqueia a estação de trabalho."""

    _check_windows()

    result = ctypes.windll.user32.LockWorkStation()

    if result == 0:
        raise RuntimeError(
            "Não foi possível bloquear a estação de trabalho."
        )


def shutdown_computer(
    delay_seconds: int = 30,
) -> None:
    """Agenda o desligamento do computador."""

    if delay_seconds < 0:
        raise ValueError(
            "O tempo de atraso não pode ser negativo."
        )

    _run_shutdown_command(
        [
            "/s",
            "/t",
            str(delay_seconds),
        ]
    )


def restart_computer(
    delay_seconds: int = 30,
) -> None:
    """Agenda o reinício do computador."""

    if delay_seconds < 0:
        raise ValueError(
            "O tempo de atraso não pode ser negativo."
        )

    _run_shutdown_command(
        [
            "/r",
            "/t",
            str(delay_seconds),
        ]
    )


def cancel_shutdown() -> None:
    """Cancela desligamento ou reinício programado."""

    _run_shutdown_command(
        [
            "/a",
        ]
    )


def get_computer_action_status() -> dict:
    """Retorna as ações disponíveis no sistema."""

    is_windows = (
        platform.system() == "Windows"
    )

    return {
        "platform": platform.system(),
        "supports_lock": is_windows,
        "supports_shutdown": is_windows,
        "supports_restart": is_windows,
        "supports_cancel_shutdown": is_windows,
    }