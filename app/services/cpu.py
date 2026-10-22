import psutil


_cpu_initialized = False


def get_cpu_info() -> dict:
    """
    Retorna informações do processador sem bloquear
    a interface gráfica.

    O psutil.cpu_percent(interval=None) não espera
    durante a chamada.
    """

    global _cpu_initialized

    # Primeira chamada serve apenas para inicializar
    # a medição do psutil.
    if not _cpu_initialized:

        psutil.cpu_percent(
            interval=None
        )

        _cpu_initialized = True

    usage_percent = psutil.cpu_percent(
        interval=None
    )

    physical_cores = psutil.cpu_count(
        logical=False
    )

    logical_cores = psutil.cpu_count(
        logical=True
    )

    frequency = psutil.cpu_freq()

    frequency_mhz = (
        round(
            frequency.current,
            2,
        )
        if frequency
        else None
    )

    return {
        "usage_percent": usage_percent,
        "physical_cores": physical_cores,
        "logical_cores": logical_cores,
        "frequency_mhz": frequency_mhz,
    }