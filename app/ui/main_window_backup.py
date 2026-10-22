import psutil

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.monitor import (
    get_network_data,
    get_network_speed_data,
    get_process_data,
    get_service_data,
    get_system_data,
    monitor,
)

from app.ui.dashboard_page import DashboardPage
from app.ui.services_page import ServicesPage


class MainWindow(QMainWindow):
    """Janela principal do SysView."""

    DASHBOARD_PAGE = 0
    COMPUTER_PAGE = 1
    CPU_PAGE = 2
    MEMORY_PAGE = 3
    DISK_PAGE = 4
    NETWORK_PAGE = 5
    PROCESS_PAGE = 6
    SERVICES_PAGE = 7

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "SysView"
        )

        self.resize(
            1250,
            800,
        )

        self.pages = QStackedWidget()

        self.menu = QListWidget()

        self.processes_data = []

        self.network_history = []

        self.setup_ui()

        self.setup_timer()

    # =========================================================
    # INTERFACE PRINCIPAL
    # =========================================================

    def setup_ui(self):
        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout.setSpacing(
            0
        )

        self.menu.setFixedWidth(
            210
        )

        self.menu.addItems(
            [
                "Dashboard",
                "Computador",
                "CPU",
                "Memória",
                "Disco",
                "Rede",
                "Processos",
                "Serviços",
            ]
        )

        self.menu.currentRowChanged.connect(
            self.change_page
        )

        main_layout.addWidget(
            self.menu
        )

        main_layout.addWidget(
            self.pages
        )

        # =====================================================
        # PÁGINAS
        # =====================================================

        self.dashboard_page = (
            DashboardPage()
        )

        self.pages.addWidget(
            self.dashboard_page
        )

        self.pages.addWidget(
            self.create_computer_page()
        )

        self.pages.addWidget(
            self.create_cpu_page()
        )

        self.pages.addWidget(
            self.create_memory_page()
        )

        self.pages.addWidget(
            self.create_disk_page()
        )

        self.pages.addWidget(
            self.create_network_page()
        )

        self.pages.addWidget(
            self.create_process_page()
        )

        self.services_page = (
            ServicesPage()
        )

        self.pages.addWidget(
            self.services_page
        )

        self.menu.setCurrentRow(
            self.DASHBOARD_PAGE
        )

    # =========================================================
    # TIMER
    # =========================================================

    def setup_timer(self):
        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.update_current_page
        )

        self.timer.start(
            1000
        )

    # =========================================================
    # TROCA DE PÁGINA
    # =========================================================

    def change_page(
        self,
        index,
    ):
        self.pages.setCurrentIndex(
            index
        )

        QTimer.singleShot(
            0,
            self.update_current_page,
        )

    # =========================================================
    # ATUALIZAÇÃO DA PÁGINA
    # =========================================================

    def update_current_page(self):
        index = (
            self.pages.currentIndex()
        )

        try:

            if index == self.DASHBOARD_PAGE:
                return

            if index == self.COMPUTER_PAGE:
                self.update_computer_page()
                return

            if index == self.CPU_PAGE:
                self.update_cpu_page()
                return

            if index == self.MEMORY_PAGE:
                self.update_memory_page()
                return

            if index == self.DISK_PAGE:
                self.update_disk_page()
                return

            if index == self.NETWORK_PAGE:
                self.update_network_page()
                return

            if index == self.PROCESS_PAGE:
                self.update_process_page()
                return

            if index == self.SERVICES_PAGE:
                self.update_services_page()
                return

        except Exception as error:

            print(
                "Erro ao atualizar página:",
                error,
            )

    # =========================================================
    # TÍTULO
    # =========================================================

    def make_title(
        self,
        text,
        subtitle=None,
    ):
        widget = QWidget()

        layout = QVBoxLayout(
            widget
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            10,
        )

        title = QLabel(
            text
        )

        title.setStyleSheet(
            "font-size: 26px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        if subtitle:

            label = QLabel(
                subtitle
            )

            layout.addWidget(
                label
            )

        return widget

    # =========================================================
    # CARD AUXILIAR
    # =========================================================

    def create_info_card(
        self,
        title,
        key,
    ):
        frame = QFrame()

        frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        layout = QVBoxLayout(
            frame
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            "font-size: 13px; "
            "font-weight: bold;"
        )

        value_label = QLabel(
            "-"
        )

        value_label.setWordWrap(
            True
        )

        value_label.setStyleSheet(
            "font-size: 15px;"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        self.computer_labels[
            key
        ] = value_label

        return frame

    # =========================================================
    # COMPUTADOR
    # =========================================================

    def create_computer_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addWidget(
            self.make_title(
                "Computador",
                "Central de informações e inventário do sistema",
            )
        )

        self.computer_labels = {}

        # =====================================================
        # IDENTIFICAÇÃO
        # =====================================================

        identification_box = QFrame()

        identification_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        identification_layout = (
            QGridLayout(
                identification_box
            )
        )

        identification_title = QLabel(
            "Identificação"
        )

        identification_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        identification_layout.addWidget(
            identification_title,
            0,
            0,
            1,
            4,
        )

        identification_layout.addWidget(
            self.create_info_card(
                "Nome do computador",
                "hostname",
            ),
            1,
            0,
        )

        identification_layout.addWidget(
            self.create_info_card(
                "Usuário atual",
                "current_user",
            ),
            1,
            1,
        )

        identification_layout.addWidget(
            self.create_info_card(
                "Sistema operacional",
                "operating_system",
            ),
            1,
            2,
        )

        identification_layout.addWidget(
            self.create_info_card(
                "Versão",
                "operating_system_release",
            ),
            1,
            3,
        )

        layout.addWidget(
            identification_box
        )

        # =====================================================
        # HARDWARE
        # =====================================================

        hardware_box = QFrame()

        hardware_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        hardware_layout = (
            QGridLayout(
                hardware_box
            )
        )

        hardware_title = QLabel(
            "Hardware"
        )

        hardware_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        hardware_layout.addWidget(
            hardware_title,
            0,
            0,
            1,
            4,
        )

        hardware_layout.addWidget(
            self.create_info_card(
                "Processador",
                "processor",
            ),
            1,
            0,
            1,
            2,
        )

        hardware_layout.addWidget(
            self.create_info_card(
                "Arquitetura",
                "architecture",
            ),
            1,
            2,
        )

        hardware_layout.addWidget(
            self.create_info_card(
                "Núcleos",
                "cores",
            ),
            1,
            3,
        )

        hardware_layout.addWidget(
            self.create_info_card(
                "Memória RAM",
                "memory_total",
            ),
            2,
            0,
        )

        hardware_layout.addWidget(
            self.create_info_card(
                "GPU",
                "gpu_summary",
            ),
            2,
            1,
            1,
            3,
        )

        layout.addWidget(
            hardware_box
        )

        # =====================================================
        # SISTEMA
        # =====================================================

        system_box = QFrame()

        system_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        system_layout = (
            QGridLayout(
                system_box
            )
        )

        system_title = QLabel(
            "Sistema"
        )

        system_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        system_layout.addWidget(
            system_title,
            0,
            0,
            1,
            4,
        )

        system_layout.addWidget(
            self.create_info_card(
                "Python",
                "python_version",
            ),
            1,
            0,
        )

        system_layout.addWidget(
            self.create_info_card(
                "Inicialização",
                "boot_time",
            ),
            1,
            1,
        )

        system_layout.addWidget(
            self.create_info_card(
                "Tempo ligado",
                "uptime",
            ),
            1,
            2,
        )

        system_layout.addWidget(
            self.create_info_card(
                "Plataforma",
                "platform",
            ),
            1,
            3,
        )

        layout.addWidget(
            system_box
        )

        # =====================================================
        # ARMAZENAMENTO
        # =====================================================

        storage_title = QLabel(
            "Armazenamento"
        )

        storage_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            storage_title
        )

        self.storage_table = (
            QTableWidget()
        )

        self.storage_table.setColumnCount(
            6
        )

        self.storage_table.setHorizontalHeaderLabels(
            [
                "Unidade",
                "Ponto de montagem",
                "Sistema de arquivos",
                "Total",
                "Livre",
                "Uso",
            ]
        )

        self.storage_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.storage_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(
            self.storage_table
        )

        # =====================================================
        # REDE
        # =====================================================

        network_title = QLabel(
            "Adaptadores de rede"
        )

        network_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            network_title
        )

        self.computer_network_table = (
            QTableWidget()
        )

        self.computer_network_table.setColumnCount(
            6
        )

        self.computer_network_table.setHorizontalHeaderLabels(
            [
                "Interface",
                "Status",
                "Velocidade",
                "IPv4",
                "IPv6",
                "MAC",
            ]
        )

        self.computer_network_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.computer_network_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(
            self.computer_network_table
        )

        layout.addStretch()

        return page

    # =========================================================
    # ATUALIZAR COMPUTADOR
    # =========================================================

    def update_computer_page(self):

        data = get_system_data()

        # -----------------------------------------------------
        # IDENTIFICAÇÃO
        # -----------------------------------------------------

        self.computer_labels[
            "hostname"
        ].setText(
            str(
                data.get(
                    "hostname",
                    "-",
                )
            )
        )

        self.computer_labels[
            "current_user"
        ].setText(
            str(
                data.get(
                    "current_user",
                    "-",
                )
            )
        )

        self.computer_labels[
            "operating_system"
        ].setText(
            str(
                data.get(
                    "operating_system",
                    "-",
                )
            )
        )

        self.computer_labels[
            "operating_system_release"
        ].setText(
            str(
                data.get(
                    "operating_system_release",
                    "-",
                )
            )
        )

        # -----------------------------------------------------
        # HARDWARE
        # -----------------------------------------------------

        self.computer_labels[
            "processor"
        ].setText(
            str(
                data.get(
                    "processor",
                    "Desconhecido",
                )
            )
        )

        self.computer_labels[
            "architecture"
        ].setText(
            str(
                data.get(
                    "architecture",
                    "-",
                )
            )
        )

        physical = data.get(
            "physical_cores",
            "-",
        )

        logical = data.get(
            "logical_cores",
            "-",
        )

        frequency = data.get(
            "frequency_mhz"
        )

        frequency_text = (
            f"{frequency:.0f} MHz"
            if frequency is not None
            else "N/D"
        )

        self.computer_labels[
            "cores"
        ].setText(
            f"{physical} físicos / "
            f"{logical} lógicos\n"
            f"{frequency_text}"
        )

        self.computer_labels[
            "memory_total"
        ].setText(
            f'{data.get("memory_total_gb", 0):.2f} GB'
        )

        # -----------------------------------------------------
        # GPU
        # -----------------------------------------------------

        gpus = data.get(
            "gpus",
            [],
        )

        if gpus:

            gpu_lines = []

            for gpu in gpus:

                name = gpu.get(
                    "name",
                    "Desconhecida",
                )

                memory = gpu.get(
                    "memory_gb"
                )

                if memory is not None:
                    gpu_lines.append(
                        f"{name} "
                        f"({memory:.2f} GB)"
                    )
                else:
                    gpu_lines.append(
                        name
                    )

            gpu_text = "\n".join(
                gpu_lines
            )

        else:

            gpu_text = (
                "GPU não identificada"
            )

        self.computer_labels[
            "gpu_summary"
        ].setText(
            gpu_text
        )

        # -----------------------------------------------------
        # SISTEMA
        # -----------------------------------------------------

        self.computer_labels[
            "python_version"
        ].setText(
            str(
                data.get(
                    "python_version",
                    "-",
                )
            )
        )

        self.computer_labels[
            "boot_time"
        ].setText(
            str(
                data.get(
                    "boot_time",
                    "-",
                )
            )
        )

        self.computer_labels[
            "uptime"
        ].setText(
            str(
                data.get(
                    "uptime",
                    "-",
                )
            )
        )

        self.computer_labels[
            "platform"
        ].setText(
            str(
                data.get(
                    "platform",
                    "-",
                )
            )
        )

        # -----------------------------------------------------
        # ARMAZENAMENTO
        # -----------------------------------------------------

        partitions = data.get(
            "partitions",
            [],
        )

        self.storage_table.setRowCount(
            len(partitions)
        )

        for row, partition in enumerate(
            partitions
        ):

            values = [
                partition.get(
                    "device",
                    "-",
                ),
                partition.get(
                    "mountpoint",
                    "-",
                ),
                partition.get(
                    "filesystem",
                    "-",
                ),
                (
                    f'{partition.get("total_gb", 0):.2f} GB'
                ),
                (
                    f'{partition.get("free_gb", 0):.2f} GB'
                ),
                (
                    f'{partition.get("usage_percent", 0):.1f}%'
                ),
            ]

            for column, value in enumerate(
                values
            ):

                self.storage_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

        self.storage_table.resizeColumnsToContents()

        # -----------------------------------------------------
        # ADAPTADORES DE REDE
        # -----------------------------------------------------

        adapters = data.get(
            "network_adapters",
            [],
        )

        self.computer_network_table.setRowCount(
            len(adapters)
        )

        for row, adapter in enumerate(
            adapters
        ):

            ipv4 = adapter.get(
                "ipv4",
                [],
            )

            ipv6 = adapter.get(
                "ipv6",
                [],
            )

            ipv4_text = (
                ", ".join(ipv4)
                if ipv4
                else "-"
            )

            ipv6_text = (
                ", ".join(ipv6)
                if ipv6
                else "-"
            )

            speed = adapter.get(
                "speed_mbps",
                0,
            )

            speed_text = (
                f"{speed} Mbps"
                if speed
                else "-"
            )

            values = [
                adapter.get(
                    "name",
                    "-",
                ),
                (
                    "Ativa"
                    if adapter.get(
                        "is_up"
                    )
                    else "Inativa"
                ),
                speed_text,
                ipv4_text,
                ipv6_text,
                adapter.get(
                    "mac"
                ) or "-",
            ]

            for column, value in enumerate(
                values
            ):

                self.computer_network_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

        self.computer_network_table.resizeColumnsToContents()

    # =========================================================
    # CPU
    # =========================================================

    def create_cpu_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addWidget(
            self.make_title(
                "CPU",
                "Uso e informações do processador",
            )
        )

        self.cpu_usage_label = QLabel(
            "0.0%"
        )

        self.cpu_usage_label.setStyleSheet(
            "font-size: 36px; "
            "font-weight: bold;"
        )

        self.cpu_progress = (
            QProgressBar()
        )

        self.cpu_progress.setRange(
            0,
            100,
        )

        self.cpu_info_label = QLabel(
            "Carregando..."
        )

        layout.addWidget(
            self.cpu_usage_label
        )

        layout.addWidget(
            self.cpu_progress
        )

        layout.addWidget(
            self.cpu_info_label
        )

        layout.addStretch()

        return page

    def update_cpu_page(self):

        data = monitor.get_dashboard()

        cpu = data[
            "cpu"
        ]

        usage = cpu.get(
            "usage_percent",
            0,
        )

        physical = cpu.get(
            "physical_cores",
            "-",
        )

        logical = cpu.get(
            "logical_cores",
            "-",
        )

        frequency = cpu.get(
            "frequency_mhz"
        )

        self.cpu_usage_label.setText(
            f"{usage:.1f}%"
        )

        self.cpu_progress.setValue(
            max(
                0,
                min(
                    100,
                    int(usage),
                ),
            )
        )

        frequency_text = (
            f"{frequency:.2f} MHz"
            if frequency is not None
            else "Indisponível"
        )

        self.cpu_info_label.setText(
            f"Núcleos físicos: {physical} • "
            f"Núcleos lógicos: {logical} • "
            f"Frequência atual: {frequency_text}"
        )

    # =========================================================
    # MEMÓRIA
    # =========================================================

    def create_memory_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addWidget(
            self.make_title(
                "Memória",
                "Uso da memória RAM",
            )
        )

        self.memory_usage_label = QLabel(
            "0.0%"
        )

        self.memory_usage_label.setStyleSheet(
            "font-size: 36px; "
            "font-weight: bold;"
        )

        self.memory_progress = (
            QProgressBar()
        )

        self.memory_progress.setRange(
            0,
            100,
        )

        self.memory_info_label = QLabel(
            "Carregando..."
        )

        layout.addWidget(
            self.memory_usage_label
        )

        layout.addWidget(
            self.memory_progress
        )

        layout.addWidget(
            self.memory_info_label
        )

        layout.addStretch()

        return page

    def update_memory_page(self):

        data = monitor.get_dashboard()

        memory = data[
            "memory"
        ]

        usage = memory.get(
            "usage_percent",
            0,
        )

        used = memory.get(
            "used_gb",
            0,
        )

        total = memory.get(
            "total_gb",
            0,
        )

        available = memory.get(
            "available_gb",
            0,
        )

        self.memory_usage_label.setText(
            f"{usage:.1f}%"
        )

        self.memory_progress.setValue(
            max(
                0,
                min(
                    100,
                    int(usage),
                ),
            )
        )

        self.memory_info_label.setText(
            f"Usado: {used:.2f} GB • "
            f"Disponível: {available:.2f} GB • "
            f"Total: {total:.2f} GB"
        )

    # =========================================================
    # DISCO
    # =========================================================

    def create_disk_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addWidget(
            self.make_title(
                "Disco",
                "Uso do armazenamento principal",
            )
        )

        self.disk_usage_label = QLabel(
            "0.0%"
        )

        self.disk_usage_label.setStyleSheet(
            "font-size: 36px; "
            "font-weight: bold;"
        )

        self.disk_progress = (
            QProgressBar()
        )

        self.disk_progress.setRange(
            0,
            100,
        )

        self.disk_info_label = QLabel(
            "Carregando..."
        )

        layout.addWidget(
            self.disk_usage_label
        )

        layout.addWidget(
            self.disk_progress
        )

        layout.addWidget(
            self.disk_info_label
        )

        layout.addStretch()

        return page

    def update_disk_page(self):

        data = monitor.get_dashboard()

        disk = data[
            "disk"
        ]

        usage = disk.get(
            "usage_percent",
            0,
        )

        used = disk.get(
            "used_gb",
            0,
        )

        total = disk.get(
            "total_gb",
            0,
        )

        free = disk.get(
            "free_gb",
            0,
        )

        self.disk_usage_label.setText(
            f"{usage:.1f}%"
        )

        self.disk_progress.setValue(
            max(
                0,
                min(
                    100,
                    int(usage),
                ),
            )
        )

        self.disk_info_label.setText(
            f"Usado: {used:.2f} GB • "
            f"Livre: {free:.2f} GB • "
            f"Total: {total:.2f} GB"
        )

    # =========================================================
    # REDE
    # =========================================================

    def create_network_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addWidget(
            self.make_title(
                "Rede",
                "Interfaces, tráfego e velocidade da conexão",
            )
        )

        self.network_table = (
            QTableWidget()
        )

        self.network_table.setColumnCount(
            6
        )

        self.network_table.setHorizontalHeaderLabels(
            [
                "Interface",
                "Ativa",
                "Velocidade",
                "IPv4",
                "IPv6",
                "MAC",
            ]
        )

        self.network_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.network_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(
            self.network_table
        )

        speed_layout = QGridLayout()

        upload_box = QFrame()

        upload_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        upload_layout = QVBoxLayout(
            upload_box
        )

        upload_title = QLabel(
            "UPLOAD"
        )

        upload_title.setStyleSheet(
            "font-size: 13px; "
            "font-weight: bold;"
        )

        self.network_upload_label = QLabel(
            "0 B/s"
        )

        self.network_upload_label.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        upload_layout.addWidget(
            upload_title
        )

        upload_layout.addWidget(
            self.network_upload_label
        )

        download_box = QFrame()

        download_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        download_layout = QVBoxLayout(
            download_box
        )

        download_title = QLabel(
            "DOWNLOAD"
        )

        download_title.setStyleSheet(
            "font-size: 13px; "
            "font-weight: bold;"
        )

        self.network_download_label = QLabel(
            "0 B/s"
        )

        self.network_download_label.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        download_layout.addWidget(
            download_title
        )

        download_layout.addWidget(
            self.network_download_label
        )

        speed_layout.addWidget(
            upload_box,
            0,
            0,
        )

        speed_layout.addWidget(
            download_box,
            0,
            1,
        )

        layout.addLayout(
            speed_layout
        )

        self.network_status = QLabel(
            "Carregando..."
        )

        layout.addWidget(
            self.network_status
        )

        self.network_plot = None

        self.network_curve_upload = None

        self.network_curve_download = None

        self.network_history = []

        try:

            import pyqtgraph as pg

            self.network_plot = (
                pg.PlotWidget()
            )

            self.network_plot.setBackground(
                None
            )

            self.network_plot.setTitle(
                "Tráfego de rede em tempo real",
                size="12pt",
            )

            self.network_plot.setLabel(
                "left",
                "Bytes/s",
            )

            self.network_plot.setLabel(
                "bottom",
                "Amostras",
            )

            self.network_plot.showGrid(
                x=True,
                y=True,
                alpha=0.2,
            )

            self.network_plot.setMinimumHeight(
                260
            )

            self.network_curve_upload = (
                self.network_plot.plot(
                    name="Upload"
                )
            )

            self.network_curve_download = (
                self.network_plot.plot(
                    name="Download"
                )
            )

            layout.addWidget(
                self.network_plot
            )

        except ImportError:

            layout.addWidget(
                QLabel(
                    "PyQtGraph não está disponível."
                )
            )

        return page

    def update_network_page(self):

        data = get_network_data()

        self.network_table.setRowCount(
            len(data)
        )

        for row, interface in enumerate(
            data
        ):

            values = [
                interface.get(
                    "name",
                    "-",
                ),
                (
                    "Sim"
                    if interface.get(
                        "is_up"
                    )
                    else "Não"
                ),
                (
                    f"{interface.get('speed_mbps', 0)} "
                    "Mbps"
                ),
                interface.get(
                    "ipv4"
                ) or "-",
                interface.get(
                    "ipv6"
                ) or "-",
                interface.get(
                    "mac"
                ) or "-",
            ]

            for column, value in enumerate(
                values
            ):

                self.network_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

        self.update_network_speed()

    def update_network_speed(self):

        speed = (
            get_network_speed_data()
        )

        total_upload = sum(
            item.get(
                "upload_bps",
                0,
            )
            for item in speed.values()
        )

        total_download = sum(
            item.get(
                "download_bps",
                0,
            )
            for item in speed.values()
        )

        self.network_upload_label.setText(
            self.format_bytes(
                total_upload
            )
            + "/s"
        )

        self.network_download_label.setText(
            self.format_bytes(
                total_download
            )
            + "/s"
        )

        self.network_status.setText(
            "Upload: "
            f"{self.format_bytes(total_upload)}/s"
            " • "
            "Download: "
            f"{self.format_bytes(total_download)}/s"
        )

        self.network_history.append(
            (
                total_upload,
                total_download,
            )
        )

        if len(
            self.network_history
        ) > 60:

            self.network_history.pop(
                0
            )

        if (
            self.network_curve_upload
            is not None
            and
            self.network_curve_download
            is not None
        ):

            upload_values = [
                item[0]
                for item
                in self.network_history
            ]

            download_values = [
                item[1]
                for item
                in self.network_history
            ]

            self.network_curve_upload.setData(
                upload_values
            )

            self.network_curve_download.setData(
                download_values
            )

    # =========================================================
    # PROCESSOS
    # =========================================================

    def create_process_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addWidget(
            self.make_title(
                "Processos",
                "Processos em execução no Windows",
            )
        )

        controls = QHBoxLayout()

        self.process_search = (
            QLineEdit()
        )

        self.process_search.setPlaceholderText(
            "Pesquisar processo..."
        )

        self.process_search.textChanged.connect(
            self.filter_processes
        )

        refresh_button = QPushButton(
            "Atualizar"
        )

        refresh_button.clicked.connect(
            self.force_refresh_processes
        )

        controls.addWidget(
            self.process_search
        )

        controls.addWidget(
            refresh_button
        )

        layout.addLayout(
            controls
        )

        self.process_table = (
            QTableWidget()
        )

        self.process_table.setColumnCount(
            7
        )

        self.process_table.setHorizontalHeaderLabels(
            [
                "PID",
                "Nome",
                "Usuário",
                "CPU %",
                "Memória %",
                "Status",
                "Threads",
            ]
        )

        self.process_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.process_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(
            self.process_table
        )

        self.process_status = QLabel(
            "Carregando..."
        )

        layout.addWidget(
            self.process_status
        )

        return page

    def update_process_page(self):

        processes = (
            get_process_data()
        )

        self.processes_data = (
            processes
        )

        self.populate_process_table(
            processes
        )

    def force_refresh_processes(
        self,
    ):

        processes = (
            monitor.force_refresh_processes()
        )

        self.processes_data = (
            processes
        )

        self.populate_process_table(
            processes
        )

    def populate_process_table(
        self,
        processes,
    ):

        search = (
            self.process_search
            .text()
            .strip()
            .lower()
        )

        if search:

            processes = [
                process
                for process
                in processes
                if search
                in str(
                    process.get(
                        "name"
                    )
                    or ""
                ).lower()
            ]

        self.process_table.setRowCount(
            len(processes)
        )

        for row, process in enumerate(
            processes
        ):

            values = [
                process.get(
                    "pid",
                    "-",
                ),
                process.get(
                    "name"
                ) or "-",
                process.get(
                    "username"
                ) or "-",
                f"{process.get('cpu_percent', 0):.2f}",
                f"{process.get('memory_percent', 0):.2f}",
                process.get(
                    "status"
                ) or "-",
                process.get(
                    "num_threads"
                ) or 0,
            ]

            for column, value in enumerate(
                values
            ):

                self.process_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

        self.process_status.setText(
            f"{len(processes)} "
            "processos encontrados."
        )

    def filter_processes(
        self,
        text,
    ):

        self.populate_process_table(
            self.processes_data
        )

    # =========================================================
    # SERVIÇOS
    # =========================================================

    def update_services_page(self):

        services = (
            get_service_data()
        )

        self.services_page.services = (
            services
        )

        self.services_page.update_services_table()

    # =========================================================
    # FORMATAÇÃO
    # =========================================================

    @staticmethod
    def format_bytes(
        value,
    ):

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ]

        size = float(
            value
        )

        for unit in units:

            if size < 1024:

                return (
                    f"{size:.2f} {unit}"
                )

            size /= 1024

        return (
            f"{size:.2f} PB"
        )

    # =========================================================
    # FECHAMENTO
    # =========================================================

    def closeEvent(
        self,
        event,
    ):

        self.timer.stop()

        event.accept()


def run_app():
    """Inicia a aplicação SysView."""

    app = QApplication.instance()

    if app is None:

        app = QApplication([])

    window = MainWindow()

    window.show()

    return app.exec()


if __name__ == "__main__":

    run_app()