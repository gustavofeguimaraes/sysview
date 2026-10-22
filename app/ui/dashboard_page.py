
from collections import deque

import pyqtgraph as pg

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.data.interfaces.data_source import DataSource


class DashboardPage(QWidget):
    """Dashboard de monitoramento local ou remoto do SysView."""

    HISTORY_SIZE = 60

    COLORS = {
        "cpu": "#38BDF8",
        "memory": "#A78BFA",
        "disk": "#34D399",
    }

    def __init__(self, data_source: DataSource) -> None:
        super().__init__()

        self.data_source = data_source

        self.cpu_history = deque(maxlen=self.HISTORY_SIZE)
        self.memory_history = deque(maxlen=self.HISTORY_SIZE)
        self.disk_history = deque(maxlen=self.HISTORY_SIZE)

        self.cpu_value = QLabel("--%")
        self.memory_value = QLabel("--%")
        self.disk_value = QLabel("--%")

        self.cpu_detail = QLabel("Aguardando dados...")
        self.memory_detail = QLabel("Aguardando dados...")
        self.disk_detail = QLabel("Aguardando dados...")

        self.cpu_progress = QProgressBar()
        self.memory_progress = QProgressBar()
        self.disk_progress = QProgressBar()

        self.cpu_graph = None
        self.memory_graph = None
        self.disk_graph = None

        self.cpu_curve = None
        self.memory_curve = None
        self.disk_curve = None

        self.hostname_value = QLabel("-")
        self.os_value = QLabel("-")
        self.os_version_value = QLabel("-")
        self.processor_value = QLabel("-")
        self.architecture_value = QLabel("-")
        self.cores_value = QLabel("-")
        self.ram_value = QLabel("-")
        self.disk_total_value = QLabel("-")

        self._initial_load_done = False

        self.setup_ui()

        # Adia as consultas até o Qt iniciar seu ciclo de eventos.
        # Não elimina o custo das consultas; evita executá-las
        # durante a construção dos widgets.
        QTimer.singleShot(0, self._initial_load)

    def _initial_load(self) -> None:
        if self._initial_load_done:
            return

        self._initial_load_done = True
        self.load_system_info()
        self.update_data()

    def set_data_source(self, data_source: DataSource) -> None:
        self.data_source = data_source
        self.clear_history()
        self.load_system_info()
        self.update_data()

    def setup_ui(self) -> None:
        self.setObjectName("sysviewDashboard")

        self.setStyleSheet("""
            QWidget#sysviewDashboard {
                background-color: #0B1220;
                color: #E2E8F0;
            }

            QFrame#metricCard, QFrame#infoPanel,
            QFrame#graphPanel {
                background-color: #151F30;
                border: 1px solid #26354B;
                border-radius: 14px;
            }

            QLabel#dashboardTitle {
                color: #F8FAFC;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#dashboardSubtitle {
                color: #94A3B8;
                font-size: 13px;
            }

            QLabel#metricTitle {
                color: #94A3B8;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#metricValue {
                color: #F8FAFC;
                font-size: 32px;
                font-weight: 700;
            }

            QLabel#metricDetail {
                color: #94A3B8;
                font-size: 12px;
            }

            QLabel#sectionTitle {
                color: #F1F5F9;
                font-size: 16px;
                font-weight: 700;
            }

            QLabel#infoName {
                color: #94A3B8;
                font-size: 12px;
            }

            QLabel#infoValue {
                color: #E2E8F0;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #0B1220;
                border: none;
            }
        """)

        content = QWidget()
        content.setObjectName("sysviewDashboard")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        title = QLabel("Visão geral")
        title.setObjectName("dashboardTitle")

        subtitle = QLabel(
            "Acompanhe o desempenho e os recursos do dispositivo."
        )
        subtitle.setObjectName("dashboardSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        cards = QGridLayout()
        cards.setSpacing(14)

        cards.addWidget(
            self.create_card(
                "PROCESSADOR",
                self.cpu_value,
                self.cpu_detail,
                self.cpu_progress,
                self.COLORS["cpu"],
            ),
            0, 0,
        )

        cards.addWidget(
            self.create_card(
                "MEMÓRIA RAM",
                self.memory_value,
                self.memory_detail,
                self.memory_progress,
                self.COLORS["memory"],
            ),
            0, 1,
        )

        cards.addWidget(
            self.create_card(
                "ARMAZENAMENTO",
                self.disk_value,
                self.disk_detail,
                self.disk_progress,
                self.COLORS["disk"],
            ),
            0, 2,
        )

        layout.addLayout(cards)

        info_panel = QFrame()
        info_panel.setObjectName("infoPanel")

        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(18, 16, 18, 18)
        info_layout.setSpacing(14)

        info_title = QLabel("Informações do computador")
        info_title.setObjectName("sectionTitle")
        info_layout.addWidget(info_title)

        fields = [
            ("Nome do computador", self.hostname_value),
            ("Sistema operacional", self.os_value),
            ("Versão do sistema", self.os_version_value),
            ("Processador", self.processor_value),
            ("Arquitetura", self.architecture_value),
            ("Núcleos lógicos", self.cores_value),
            ("Memória RAM", self.ram_value),
            ("Disco", self.disk_total_value),
        ]

        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(24)
        info_grid.setVerticalSpacing(12)

        for index, (name, value) in enumerate(fields):
            row = index // 2
            column = (index % 2) * 2

            label = QLabel(name)
            label.setObjectName("infoName")

            value.setObjectName("infoValue")
            value.setWordWrap(True)
            value.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )

            info_grid.addWidget(label, row, column)
            info_grid.addWidget(value, row, column + 1)

        info_layout.addLayout(info_grid)
        layout.addWidget(info_panel)

        graphs_title = QLabel("Histórico de utilização")
        graphs_title.setObjectName("sectionTitle")
        layout.addWidget(graphs_title)

        graphs = QGridLayout()
        graphs.setSpacing(14)

        self.cpu_graph, self.cpu_curve = self.create_graph(
            "Processador", self.COLORS["cpu"]
        )

        self.memory_graph, self.memory_curve = self.create_graph(
            "Memória RAM", self.COLORS["memory"]
        )

        self.disk_graph, self.disk_curve = self.create_graph(
            "Armazenamento", self.COLORS["disk"]
        )

        graphs.addWidget(
            self._graph_panel(self.cpu_graph), 0, 0
        )
        graphs.addWidget(
            self._graph_panel(self.memory_graph), 0, 1
        )
        graphs.addWidget(
            self._graph_panel(self.disk_graph), 1, 0, 1, 2
        )

        layout.addLayout(graphs)
        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def create_card(
        self,
        title_text: str,
        value_label: QLabel,
        detail_label: QLabel,
        progress_bar: QProgressBar,
        color: str = "#38BDF8",
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        title = QLabel(title_text)
        title.setObjectName("metricTitle")

        value_label.setObjectName("metricValue")
        detail_label.setObjectName("metricDetail")
        detail_label.setWordWrap(True)

        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(8)

        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #26354B;
                border: none;
                border-radius: 4px;
            }}

            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(value_label)
        card_layout.addWidget(detail_label)
        card_layout.addStretch()
        card_layout.addWidget(progress_bar)

        card.setMinimumHeight(160)

        return card

    def _graph_panel(self, graph: pg.PlotWidget) -> QFrame:
        panel = QFrame()
        panel.setObjectName("graphPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(graph)

        return panel

    def create_graph(
        self,
        title: str,
        color: str = "#38BDF8",
    ):
        graph = pg.PlotWidget()

        graph.setBackground("#151F30")
        graph.setTitle(title, color="#E2E8F0", size="11pt")

        graph.setYRange(0, 100)
        graph.setXRange(0, self.HISTORY_SIZE, padding=0)

        graph.setLabel("left", "Uso (%)")
        graph.setLabel("bottom", "Amostras")

        graph.showGrid(x=True, y=True, alpha=0.15)

        graph.setMinimumHeight(190)

        graph.setMouseEnabled(x=False, y=False)
        graph.hideButtons()

        graph.getAxis("left").setTextPen("#94A3B8")
        graph.getAxis("bottom").setTextPen("#94A3B8")

        curve = graph.plot(
            pen=pg.mkPen(color=color, width=2)
        )

        return graph, curve

    def load_system_info(self) -> None:
        try:
            data = self.data_source.get_system() or {}

            mapping = [
                (self.hostname_value, "hostname"),
                (self.os_value, "operating_system"),
                (self.os_version_value, "operating_system_version"),
                (self.processor_value, "processor"),
                (self.architecture_value, "architecture"),
                (self.cores_value, "cpu_count"),
            ]

            for label, key in mapping:
                value = data.get(key)
                label.setText(
                    str(value) if value is not None else "-"
                )

            memory_total = data.get("memory_total_gb")
            self.ram_value.setText(
                f"{float(memory_total):.2f} GB"
                if memory_total is not None else "-"
            )

            disk_total = data.get("disk_total_gb")
            self.disk_total_value.setText(
                f"{float(disk_total):.2f} GB"
                if disk_total is not None else "-"
            )

        except Exception as error:
            self.hostname_value.setText(f"Erro: {error}")

    def update_data(self) -> None:
        try:
            data = self.data_source.get_dashboard()

            cpu = data["cpu"]
            memory = data["memory"]
            disk = data["disk"]

            cpu_usage = float(cpu["usage_percent"])
            memory_usage = float(memory["usage_percent"])
            disk_usage = float(disk["usage_percent"])

            self.cpu_history.append(cpu_usage)
            self.memory_history.append(memory_usage)
            self.disk_history.append(disk_usage)

            self.cpu_value.setText(f"{cpu_usage:.1f}%")
            self.cpu_detail.setText(
                f"{cpu.get('physical_cores', '-')} núcleos físicos"
                f" • {cpu.get('logical_cores', '-')} lógicos"
            )
            self.cpu_progress.setValue(
                self.clamp_percentage(cpu_usage)
            )

            self.memory_value.setText(f"{memory_usage:.1f}%")
            self.memory_detail.setText(
                f"{float(memory.get('used_gb', 0)):.2f} GB"
                f" de {float(memory.get('total_gb', 0)):.2f} GB"
            )
            self.memory_progress.setValue(
                self.clamp_percentage(memory_usage)
            )

            self.disk_value.setText(f"{disk_usage:.1f}%")
            self.disk_detail.setText(
                f"{float(disk.get('used_gb', 0)):.2f} GB"
                f" de {float(disk.get('total_gb', 0)):.2f} GB"
            )
            self.disk_progress.setValue(
                self.clamp_percentage(disk_usage)
            )

            self.update_graphs()

        except Exception as error:
            self.cpu_detail.setText(f"Erro: {error}")

    def update_graphs(self) -> None:
        if self.cpu_curve is not None:
            self.cpu_curve.setData(list(self.cpu_history))

        if self.memory_curve is not None:
            self.memory_curve.setData(list(self.memory_history))

        if self.disk_curve is not None:
            self.disk_curve.setData(list(self.disk_history))

    def clear_history(self) -> None:
        self.cpu_history.clear()
        self.memory_history.clear()
        self.disk_history.clear()
        self.update_graphs()

    @staticmethod
    def clamp_percentage(value: float) -> int:
        return max(0, min(100, int(value)))
