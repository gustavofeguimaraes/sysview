
import sys

from PySide6.QtWidgets import QApplication

from app.core.config import APP_NAME, APP_VERSION
from app.core.logger import setup_logger
from app.ui.main_window import MainWindow


def main() -> None:
    logger = setup_logger()

    logger.info(
        "%s iniciado - versão %s",
        APP_NAME,
        APP_VERSION,
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    try:
        window = MainWindow()
        window.show()

        logger.info("Interface gráfica iniciada com sucesso.")

        sys.exit(app.exec())

    except Exception:
        logger.exception(
            "Erro durante a inicialização da interface."
        )
        raise


if __name__ == "__main__":
    main()

