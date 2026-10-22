from collections import deque

import pyqtgraph as pg

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.data.interfaces.data_source import DataSource


class DashboardPage(QWidget):
    """
    Página principal de monitoramento do SysView.

    A página não acessa diretamente psutil ou os serviços
    do sistema. Ela recebe uma DataSource, que pode representar
    o computador local ou um dispositivo remoto.
    """

    HISTORY_SIZE = 60

    def __init__(
        self,
        data_source: DataSource,
    ) -> None:
        super().__init__()

        self.data_source = data_source

        # -----------------------------------------------------
        # HISTÓRICO
        # -----------------------------------------------------

        self.cpu_history = deque(
            maxlen=self.HISTORY_SIZE
        )

        self.memory_history = deque(
            maxlen=self.HISTORY_SIZE
        )

        self.disk_history = deque(
            maxlen=self.HISTORY_SIZE
        )

        # -----------------------------------------------------
        # VALORES
        # -----------------------------------------------------

        self.cpu_value = QLabel("0%")
        self.memory_value = QLabel("0%")
        self.disk_value = QLabel("0%")

        self.cpu_detail = QLabel(
            "Carregando..."
        )

        self.memory_detail = QLabel(
            "Carregando..."
        )

        self.disk_detail = QLabel(
            "Carregando..."
        )

        # -----------------------------------------------------
        # BARRAS
        # -----------------------------------------------------

        self.cpu_progress = QProgressBar()
        self.memory_progress = QProgressBar()
        self.disk_progress = QProgressBar()

        # -----------------------------------------------------
        # GRÁFICOS
        # -----------------------------------------------------

        self.cpu_graph = None
        self.memory_graph = None
        self.disk_graph = None

        self.cpu_curve = None
        self.memory_curve = None
        self.disk_curve = None

        # -----------------------------------------------------
        # INFORMAÇÕES DO COMPUTADOR
        # -----------------------------------------------------

        self.hostname_value = QLabel("-")
        self.os_value = QLabel("-")
        self.os_version_value = QLabel("-")
        self.processor_value = QLabel("-")
        self.architecture_value = QLabel("-")
        self.cores_value = QLabel("-")
        self.ram_value = QLabel("-")
        self.disk_total_value = QLabel("-")

        # -----------------------------------------------------
        # INTERFACE
        # -----------------------------------------------------

        self.setup_ui()

        self.load_system_info()

        # Primeira atualização
        self.update_data()

    # =========================================================
    # FONTE DE DADOS
    # =========================================================

    def set_data_source(
        self,
        data_source: DataSource,
    ) -> None:
        """
        Troca a fonte de dados do Dashboard.

        Permite mudar entre computador local e remoto
        sem precisar recriar a página.
        """

        self.data_source = data_source

        self.clear_history()

        self.load_system_info()
        self.update_data()

    # =========================================================
    # INTERFACE
    # =========================================================

    def setup_ui(self) -> None:

        layout = QVBoxLayout(self)

        title = QLabel(
            "Dashboard"
        )

        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Monitoramento em tempo real do computador"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # -----------------------------------------------------
        # CARDS
        # -----------------------------------------------------

        cards_layout = QGridLayout()

        cards_layout.addWidget(
            self.create_card(
                "CPU",
                self.cpu_value,
                self.cpu_detail,
                self.cpu_progress,
            ),
            0,
            0,
        )

        cards_layout.addWidget(
            self.create_card(
                "MEMÓRIA",
                self.memory_value,
                self.memory_detail,
                self.memory_progress,
            ),
            0,
            1,
        )

        cards_layout.addWidget(
            self.create_card(
                "DISCO",
                self.disk_value,
                self.disk_detail,
                self.disk_progress,
            ),
            0,
            2,
        )

        layout.addLayout(
            cards_layout
        )

        # -----------------------------------------------------
        # SISTEMA
        # -----------------------------------------------------

        system_box = QGroupBox(
            "Informações do computador"
        )

        system_layout = QGridLayout(
            system_box
        )

        fields = [
            (
                "Nome do computador:",
                self.hostname_value,
                0,
                0,
            ),
            (
                "Sistema operacional:",
                self.os_value,
                0,
                2,
            ),
            (
                "Versão do sistema:",
                self.os_version_value,
                1,
                0,
            ),
            (
                "Processador:",
                self.processor_value,
                1,
                2,
            ),
            (
                "Arquitetura:",
                self.architecture_value,
                2,
                0,
            ),
            (
                "Núcleos lógicos:",
                self.cores_value,
                2,
                2,
            ),
            (
                "Memória RAM:",
                self.ram_value,
                3,
                0,
            ),
            (
                "Disco:",
                self.disk_total_value,
                3,
                2,
            ),
        ]

        for (
            label_text,
            value_widget,
            row,
            column,
        ) in fields:

            system_layout.addWidget(
                QLabel(label_text),
                row,
                column,
            )

            system_layout.addWidget(
                value_widget,
                row,
                column + 1,
            )

        layout.addWidget(
            system_box
        )

        # -----------------------------------------------------
        # GRÁFICOS
        # -----------------------------------------------------

        graphs_layout = QGridLayout()

        (
            self.cpu_graph,
            self.cpu_curve,
        ) = self.create_graph(
            "Uso da CPU"
        )

        (
            self.memory_graph,
            self.memory_curve,
        ) = self.create_graph(
            "Uso da Memória"
        )

        (
            self.disk_graph,
            self.disk_curve,
        ) = self.create_graph(
            "Uso do Disco"
        )

        graphs_layout.addWidget(
            self.cpu_graph,
            0,
            0,
        )

        graphs_layout.addWidget(
            self.memory_graph,
            0,
            1,
        )

        graphs_layout.addWidget(
            self.disk_graph,
            1,
            0,
            1,
            2,
        )

        layout.addLayout(
            graphs_layout
        )

    # =========================================================
    # CARDS
    # =========================================================

    def create_card(
        self,
        title_text: str,
        value_label: QLabel,
        detail_label: QLabel,
        progress_bar: QProgressBar,
    ) -> QFrame:

        card = QFrame()

        card.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        card_layout = QVBoxLayout(
            card
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet(
            "font-size: 15px; font-weight: bold;"
        )

        value_label.setStyleSheet(
            "font-size: 30px; font-weight: bold;"
        )

        detail_label.setStyleSheet(
            "font-size: 12px;"
        )

        progress_bar.setRange(
            0,
            100,
        )

        progress_bar.setTextVisible(
            False
        )

        progress_bar.setFixedHeight(
            8
        )

        card_layout.addWidget(
            title
        )

        card_layout.addWidget(
            value_label
        )

        card_layout.addWidget(
            detail_label
        )

        card_layout.addWidget(
            progress_bar
        )

        return card

    # =========================================================
    # GRÁFICOS
    # =========================================================

    def create_graph(
        self,
        title: str,
    ):

        graph = pg.PlotWidget()

        graph.setBackground(
            None
        )

        graph.setTitle(
            title,
            size="12pt",
        )

        graph.setYRange(
            0,
            100,
        )

        graph.setLabel(
            "left",
            "Uso (%)",
        )

        graph.setLabel(
            "bottom",
            "Amostras",
        )

        graph.showGrid(
            x=True,
            y=True,
            alpha=0.2,
        )

        graph.setMinimumHeight(
            220
        )

        curve = graph.plot()

        return (
            graph,
            curve,
        )

    # =========================================================
    # SISTEMA
    # =========================================================

    def load_system_info(self) -> None:
        """
        Carrega informações estáticas através da DataSource.
        """

        try:

            data = self.data_source.get_system()

            self.hostname_value.setText(
                str(
                    data.get(
                        "hostname",
                        "-",
                    )
                )
            )

            self.os_value.setText(
                str(
                    data.get(
                        "operating_system",
                        "-",
                    )
                )
            )

            self.os_version_value.setText(
                str(
                    data.get(
                        "operating_system_version",
                        "-",
                    )
                )
            )

            self.processor_value.setText(
                str(
                    data.get(
                        "processor",
                        "-",
                    )
                )
            )

            self.architecture_value.setText(
                str(
                    data.get(
                        "architecture",
                        "-",
                    )
                )
            )

            self.cores_value.setText(
                str(
                    data.get(
                        "cpu_count",
                        "-",
                    )
                )
            )

            memory_total = data.get(
                "memory_total_gb"
            )

            if memory_total is not None:
                self.ram_value.setText(
                    f"{memory_total:.2f} GB"
                )
            else:
                self.ram_value.setText("-")

            disk_total = data.get(
                "disk_total_gb"
            )

            if disk_total is not None:
                self.disk_total_value.setText(
                    f"{disk_total:.2f} GB"
                )
            else:
                self.disk_total_value.setText("-")

        except Exception as error:

            self.hostname_value.setText(
                f"Erro: {error}"
            )

    # =========================================================
    # DADOS
    # =========================================================

    def update_data(self) -> None:
        """
        Atualiza somente os dados dinâmicos.

        A origem dos dados é determinada pela DataSource.
        """

        try:

            data = (
                self.data_source.get_dashboard()
            )

            cpu = data["cpu"]
            memory = data["memory"]
            disk = data["disk"]

            cpu_usage = float(
                cpu["usage_percent"]
            )

            memory_usage = float(
                memory["usage_percent"]
            )

            disk_usage = float(
                disk["usage_percent"]
            )

            # -------------------------------------------------
            # HISTÓRICO
            # -------------------------------------------------

            self.cpu_history.append(
                cpu_usage
            )

            self.memory_history.append(
                memory_usage
            )

            self.disk_history.append(
                disk_usage
            )

            # -------------------------------------------------
            # CPU
            # -------------------------------------------------

            self.cpu_value.setText(
                f"{cpu_usage:.1f}%"
            )

            self.cpu_detail.setText(
                f"{cpu.get('physical_cores', '-')}"
                " núcleos físicos • "
                f"{cpu.get('logical_cores', '-')}"
                " lógicos"
            )

            self.cpu_progress.setValue(
                self.clamp_percentage(
                    cpu_usage
                )
            )

            # -------------------------------------------------
            # MEMÓRIA
            # -------------------------------------------------

            self.memory_value.setText(
                f"{memory_usage:.1f}%"
            )

            self.memory_detail.setText(
                f"{memory.get('used_gb', 0):.2f} GB "
                "usados de "
                f"{memory.get('total_gb', 0):.2f} GB"
            )

            self.memory_progress.setValue(
                self.clamp_percentage(
                    memory_usage
                )
            )

            # -------------------------------------------------
            # DISCO
            # -------------------------------------------------

            self.disk_value.setText(
                f"{disk_usage:.1f}%"
            )

            self.disk_detail.setText(
                f"{disk.get('used_gb', 0):.2f} GB "
                "usados de "
                f"{disk.get('total_gb', 0):.2f} GB"
            )

            self.disk_progress.setValue(
                self.clamp_percentage(
                    disk_usage
                )
            )

            # -------------------------------------------------
            # GRÁFICOS
            # -------------------------------------------------

            self.update_graphs()

        except Exception as error:

            self.cpu_detail.setText(
                f"Erro: {error}"
            )

    # =========================================================
    # GRÁFICOS
    # =========================================================

    def update_graphs(self) -> None:
        """
        Atualiza os gráficos usando o histórico da própria página.
        """

        self.cpu_curve.setData(
            list(self.cpu_history)
        )

        self.memory_curve.setData(
            list(self.memory_history)
        )

        self.disk_curve.setData(
            list(self.disk_history)
        )

    # =========================================================
    # HISTÓRICO
    # =========================================================

    def clear_history(self) -> None:
        """
        Limpa o histórico quando a fonte de dados muda.
        """

        self.cpu_history.clear()
        self.memory_history.clear()
        self.disk_history.clear()

        self.update_graphs()

    # =========================================================
    # UTILITÁRIOS
    # =========================================================

    @staticmethod
    def clamp_percentage(
        value: float,
    ) -> int:

        return max(
            0,
            min(
                100,
                int(value),
            ),
        )