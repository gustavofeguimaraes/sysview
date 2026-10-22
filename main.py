
import sys
import time
import logging

from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.config import APP_NAME, APP_VERSION
from app.core.logger import setup_logger

from app.data.models.device_manager import DeviceManager
from app.data.database.device_repository import DeviceRepository

from app.ui.main_window import MainWindow


logger = logging.getLogger(__name__)


def initialize_device_manager():
    start = time.perf_counter()

    try:
        manager = DeviceManager(
            repository=DeviceRepository(),
            auto_load=True,
        )

        elapsed = time.perf_counter() - start

        logger.info(
            "MySQL carregado em %.3f segundos. "
            "%d dispositivo(s) encontrado(s).",
            elapsed,
            manager.count(),
        )

        return manager, True

    except Exception:
        elapsed = time.perf_counter() - start

        logger.exception(
            "Falha ao carregar MySQL após %.3f segundos.",
            elapsed,
        )

        return DeviceManager(), False


def main() -> None:
    total_start = time.perf_counter()

    setup_logger()

    logger.info(
        "%s iniciado - versão %s",
        APP_NAME,
        APP_VERSION,
    )

    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    try:
        database_start = time.perf_counter()

        device_manager, database_available = (
            initialize_device_manager()
        )

        logger.info(
            "Etapa de banco: %.3f segundos.",
            time.perf_counter() - database_start,
        )

        window_start = time.perf_counter()

        window = MainWindow()

        window.device_manager = device_manager

        logger.info(
            "Construção da interface: %.3f segundos.",
            time.perf_counter() - window_start,
        )

        show_start = time.perf_counter()

        window.show()

        app.processEvents()

        logger.info(
            "Exibição inicial: %.3f segundos.",
            time.perf_counter() - show_start,
        )

        logger.info(
            "Inicialização até exibição: %.3f segundos.",
            time.perf_counter() - total_start,
        )

        if not database_available:
            QMessageBox.warning(
                window,
                "SysView - MySQL indisponível",
                "Não foi possível conectar ao MySQL.\n\n"
                "O monitoramento local continuará funcionando.\n"
                "Os novos cadastros não serão persistidos.",
            )

        logger.info(
            "Interface gráfica iniciada com sucesso."
        )

        return app.exec()

    except Exception:
        logger.exception(
            "Erro durante a inicialização da interface."
        )
        raise


if __name__ == "__main__":
    sys.exit(main())
