
import psutil

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType
from app.data.sources.factory import SourceFactory

from app.ui.dashboard_page import DashboardPage
from app.ui.services_page import ServicesPage
from app.ui.network_connections_page import (
    NetworkConnectionsPage,
)


class MainWindow(QMainWindow):
    """Janela principal do SysView."""

    DASHBOARD_PAGE = 0
    COMPUTER_PAGE = 1
    CPU_PAGE = 2
    MEMORY_PAGE = 3
    DISK_PAGE = 4
    NETWORK_PAGE = 5
    NETWORK_CONNECTIONS_PAGE = 6
    PROCESS_PAGE = 7
    SERVICES_PAGE = 8

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SysView")
        self.resize(1250, 800)
        self.setMinimumSize(1000, 650)
        self.setObjectName("sysviewMainWindow")
        self.apply_theme()

        # =====================================================
        # DISPOSITIVO ATUAL
        # =====================================================

        self.current_device = Device(
            device_id="local",
            name="Computador local",
            device_type=DeviceType.COMPUTER,
            platform=PlatformType.WINDOWS,
            connection_type=ConnectionType.LOCAL,
            online=True,
        )

        # =====================================================
        # FONTES DE DADOS E CONTROLE
        # =====================================================

        self.data_source = (
            SourceFactory.create_data_source(
                self.current_device
            )
        )

        self.control_source = (
            SourceFactory.create_control_source(
                self.current_device
            )
        )

        # =====================================================
        # INTERFACE
        # =====================================================

        self.pages = QStackedWidget()
        self.menu = QListWidget()

        # =====================================================
        # PROCESSOS
        # =====================================================

        self.processes_data = []
        self.selected_process_pid = None
        self.process_table_signature = None
        self.process_search_text = ""
        self.process_sort_column = None
        self.process_sort_order = (
            Qt.SortOrder.AscendingOrder
        )

        # =====================================================
        # REDE
        # =====================================================

        self.network_history = []

        # =====================================================
        # CONFIGURAÇÃO
        # =====================================================

        self.setup_ui()
        self.setup_timer()

    def apply_theme(self):
        """Tema global: mantém a lógica das páginas e padroniza seus widgets."""
        self.setStyleSheet("""
            QMainWindow#sysviewMainWindow, QWidget#sysviewContent,
            QStackedWidget {
                background-color: #0B1220;
                color: #E2E8F0;
            }
            QWidget {
                color: #E2E8F0;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QFrame#sysviewSidebar {
                background-color: #111B2B;
                border-right: 1px solid #26354B;
            }
            QLabel#sysviewBrand {
                font-size: 23px;
                font-weight: 800;
                color: #F8FAFC;
                padding-left: 8px;
            }
            QLabel#sysviewBrandSubtitle, QLabel#sysviewNavigationTitle,
            QLabel#sysviewDeviceCaption, QLabel#sysviewFooter {
                color: #8192AA;
                font-size: 10px;
                font-weight: 600;
                padding-left: 8px;
            }
            QListWidget#sysviewNavigation {
                background: transparent;
                border: none;
                outline: none;
                padding: 0;
            }
            QListWidget#sysviewNavigation::item {
                color: #AEBED3;
                min-height: 38px;
                padding: 4px 12px;
                border-radius: 8px;
                margin-bottom: 2px;
            }
            QListWidget#sysviewNavigation::item:hover {
                background-color: #1C2B42;
                color: #FFFFFF;
            }
            QListWidget#sysviewNavigation::item:selected {
                background-color: #1D3B5C;
                color: #7DD3FC;
                border-left: 3px solid #38BDF8;
                font-weight: 700;
            }
            QFrame#sysviewDeviceCard {
                background-color: #19273B;
                border: 1px solid #2B405A;
                border-radius: 10px;
            }
            QLabel#sysviewDeviceStatus, QLabel#sysviewHeaderStatus {
                color: #34D399;
                font-weight: 700;
                font-size: 11px;
            }
            QFrame#sysviewHeader {
                background-color: #101A29;
                border-bottom: 1px solid #26354B;
            }
            QLabel#sysviewHeaderTitle {
                color: #F8FAFC;
                font-size: 17px;
                font-weight: 700;
            }
            QFrame#sysviewPanel, QGroupBox {
                background-color: #151F30;
                border: 1px solid #26354B;
                border-radius: 10px;
            }
            QGroupBox {
                margin-top: 12px;
                padding-top: 14px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #E2E8F0;
            }
            QTableWidget {
                background-color: #151F30;
                alternate-background-color: #19263A;
                color: #DCE7F5;
                gridline-color: #26354B;
                border: 1px solid #26354B;
                border-radius: 8px;
                selection-background-color: #24537A;
                selection-color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #1D2D43;
                color: #CBD5E1;
                border: none;
                border-right: 1px solid #314259;
                border-bottom: 1px solid #314259;
                padding: 8px;
                font-weight: 600;
            }
            QTableCornerButton::section {
                background-color: #1D2D43;
                border: none;
            }
            QLineEdit, QComboBox {
                background-color: #172338;
                color: #F1F5F9;
                border: 1px solid #30435D;
                border-radius: 7px;
                padding: 7px 10px;
                min-height: 19px;
                selection-background-color: #2563A0;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #38BDF8;
            }
            QComboBox QAbstractItemView {
                background-color: #172338;
                color: #F1F5F9;
                selection-background-color: #24537A;
            }
            QPushButton {
                background-color: #243750;
                color: #E2E8F0;
                border: 1px solid #344B68;
                border-radius: 7px;
                padding: 8px 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #315276;
                border-color: #38BDF8;
            }
            QPushButton:pressed { background-color: #1B344E; }
            QPushButton:disabled {
                background-color: #192435;
                color: #65768B;
                border-color: #26354B;
            }
            QPushButton#dangerButton {
                background-color: #5B2835;
                border-color: #934354;
                color: #FFE4E6;
            }
            QPushButton#dangerButton:hover {
                background-color: #7A3042;
            }
            QProgressBar {
                background-color: #26354B;
                border: none;
                border-radius: 5px;
                min-height: 9px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #38BDF8;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background: #111B2B;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #344861;
                border-radius: 5px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
            QMessageBox { background-color: #151F30; }
        """)

    # =========================================================
    # INTERFACE PRINCIPAL
    # =========================================================

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout.setSpacing(0)

        # -----------------------------------------------------
        # MENU
        # -----------------------------------------------------

        self.menu.setFixedWidth(218)
        self.menu.setObjectName("sysviewNavigation")
        self.menu.setSpacing(4)
        self.menu.setFrameShape(QFrame.Shape.NoFrame)

        self.menu.addItems(
            [
                "Dashboard",
                "Computador",
                "CPU",
                "Memória",
                "Disco",
                "Rede",
                "Conexões",
                "Processos",
                "Serviços",
            ]
        )

        self.menu.currentRowChanged.connect(
            self.change_page
        )

        # Menu lateral com identidade visual própria.
        sidebar = QFrame()
        sidebar.setObjectName("sysviewSidebar")
        sidebar.setFixedWidth(242)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 14)
        sidebar_layout.setSpacing(12)

        brand = QLabel("◈  SYSVIEW")
        brand.setObjectName("sysviewBrand")
        sidebar_layout.addWidget(brand)

        brand_subtitle = QLabel("CENTRAL DE MONITORAMENTO")
        brand_subtitle.setObjectName("sysviewBrandSubtitle")
        sidebar_layout.addWidget(brand_subtitle)

        navigation_label = QLabel("NAVEGAÇÃO")
        navigation_label.setObjectName("sysviewNavigationTitle")
        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(navigation_label)
        sidebar_layout.addWidget(self.menu, 1)

        device_card = QFrame()
        device_card.setObjectName("sysviewDeviceCard")
        device_layout = QVBoxLayout(device_card)
        device_layout.setContentsMargins(12, 12, 12, 12)
        device_layout.setSpacing(5)
        device_label = QLabel("DISPOSITIVO ATUAL")
        device_label.setObjectName("sysviewDeviceCaption")
        self.device_status_label = QLabel("●  Computador local")
        self.device_status_label.setObjectName("sysviewDeviceStatus")
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_status_label)
        sidebar_layout.addWidget(device_card)

        footer = QLabel("SysView  •  Monitoramento")
        footer.setObjectName("sysviewFooter")
        sidebar_layout.addWidget(footer)

        main_layout.addWidget(sidebar)

        # Cabeçalho global para todas as páginas.
        content = QWidget()
        content.setObjectName("sysviewContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("sysviewHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 12, 24, 12)

        self.header_page_label = QLabel("Dashboard")
        self.header_page_label.setObjectName("sysviewHeaderTitle")
        header_layout.addWidget(self.header_page_label)
        header_layout.addStretch()

        header_status = QLabel("●  MONITORAMENTO LOCAL")
        header_status.setObjectName("sysviewHeaderStatus")
        header_layout.addWidget(header_status)

        content_layout.addWidget(header)
        content_layout.addWidget(self.pages, 1)
        main_layout.addWidget(content, 1)

        # -----------------------------------------------------
        # DASHBOARD
        # -----------------------------------------------------

        self.dashboard_page = DashboardPage(
            data_source=self.data_source
        )

        self.pages.addWidget(
            self.dashboard_page
        )

        # -----------------------------------------------------
        # OUTRAS PÁGINAS
        # -----------------------------------------------------

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

        self.network_connections_page = NetworkConnectionsPage(
            data_source=self.data_source
        )

        self.pages.addWidget(
            self.network_connections_page
        )

        self.pages.addWidget(
            self.create_process_page()
        )

        self.services_page = ServicesPage(
            data_source=self.data_source,
            control_source=self.control_source,
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
        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_current_page
        )

        self.timer.start(1000)

    # =========================================================
    # NAVEGAÇÃO
    # =========================================================

    def change_page(
        self,
        index,
    ):
        if index < 0 or index >= self.pages.count():
            return

        self.pages.setCurrentIndex(
            index
        )

        if hasattr(self, "header_page_label"):
            item = self.menu.item(index)
            if item is not None:
                self.header_page_label.setText(item.text())

        QTimer.singleShot(
            0,
            self.update_current_page,
        )

    def update_current_page(self):
        index = self.pages.currentIndex()

        try:

            if index == self.DASHBOARD_PAGE:
                self.dashboard_page.update_data()
                return

            if index == self.COMPUTER_PAGE:
                self.update_computer_page()

            elif index == self.CPU_PAGE:
                self.update_cpu_page()

            elif index == self.MEMORY_PAGE:
                self.update_memory_page()

            elif index == self.DISK_PAGE:
                self.update_disk_page()

            elif index == self.NETWORK_PAGE:
                self.update_network_page()

            elif index == self.NETWORK_CONNECTIONS_PAGE:
                self.update_network_connections_page()

            elif index == self.PROCESS_PAGE:
                self.update_process_page()

            elif index == self.SERVICES_PAGE:
                self.update_services_page()

        except Exception as error:

            print(
                "Erro ao atualizar página:",
                error,
            )

    # =========================================================
    # COMPONENTES AUXILIARES
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

        title = QLabel(text)

        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        if subtitle:
            layout.addWidget(
                QLabel(subtitle)
            )

        return widget

    def create_info_card(
        self,
        title,
        key,
    ):
        frame = QFrame()

        frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        frame.setObjectName("sysviewPanel")

        layout = QVBoxLayout(
            frame
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        value_label = QLabel("-")

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

        # -----------------------------------------------------
        # AÇÕES
        # -----------------------------------------------------

        actions_box = QFrame()

        actions_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        actions_box.setObjectName("sysviewPanel")

        actions_layout = QVBoxLayout(
            actions_box
        )

        title = QLabel(
            "Ações do computador"
        )

        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        actions_layout.addWidget(
            title
        )

        buttons = QHBoxLayout()

        self.refresh_computer_button = (
            QPushButton("Atualizar")
        )

        self.lock_computer_button = (
            QPushButton("Bloquear")
        )

        self.restart_computer_button = (
            QPushButton("Reiniciar")
        )

        self.shutdown_computer_button = (
            QPushButton("Desligar")
        )

        self.cancel_shutdown_button = (
            QPushButton("Cancelar desligamento")
        )

        self.refresh_computer_button.clicked.connect(
            self.refresh_computer_action
        )

        self.lock_computer_button.clicked.connect(
            self.lock_computer_action
        )

        self.setObjectName("dangerButton")

        self.restart_computer_button.clicked.connect(
            self.restart_computer_action
        )

        self.setObjectName("dangerButton")

        self.shutdown_computer_button.clicked.connect(
            self.shutdown_computer_action
        )

        self.cancel_shutdown_button.clicked.connect(
            self.cancel_shutdown_action
        )

        for button in (
            self.refresh_computer_button,
            self.lock_computer_button,
            self.restart_computer_button,
            self.shutdown_computer_button,
            self.cancel_shutdown_button,
        ):
            buttons.addWidget(
                button
            )

        actions_layout.addLayout(
            buttons
        )

        layout.addWidget(
            actions_box
        )

        # -----------------------------------------------------
        # IDENTIFICAÇÃO
        # -----------------------------------------------------

        self.computer_labels = {}

        identification_box = QFrame()

        identification_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        identification_box.setObjectName("sysviewPanel")

        identification_layout = QGridLayout(
            identification_box
        )

        title = QLabel(
            "Identificação"
        )

        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        identification_layout.addWidget(
            title,
            0,
            0,
            1,
            4,
        )

        for col, args in enumerate(
            (
                (
                    "Nome do computador",
                    "hostname",
                ),
                (
                    "Usuário atual",
                    "current_user",
                ),
                (
                    "Sistema operacional",
                    "operating_system",
                ),
                (
                    "Versão",
                    "operating_system_release",
                ),
            )
        ):
            identification_layout.addWidget(
                self.create_info_card(
                    *args
                ),
                1,
                col,
            )

        layout.addWidget(
            identification_box
        )

        # -----------------------------------------------------
        # HARDWARE
        # -----------------------------------------------------

        hardware_box = QFrame()

        hardware_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        hardware_box.setObjectName("sysviewPanel")

        hardware_layout = QGridLayout(
            hardware_box
        )

        title = QLabel(
            "Hardware"
        )

        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        hardware_layout.addWidget(
            title,
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

        # -----------------------------------------------------
        # SISTEMA
        # -----------------------------------------------------

        system_box = QFrame()

        system_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        system_box.setObjectName("sysviewPanel")

        system_layout = QGridLayout(
            system_box
        )

        title = QLabel(
            "Sistema"
        )

        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        system_layout.addWidget(
            title,
            0,
            0,
            1,
            4,
        )

        for col, args in enumerate(
            (
                (
                    "Python",
                    "python_version",
                ),
                (
                    "Inicialização",
                    "boot_time",
                ),
                (
                    "Tempo ligado",
                    "uptime",
                ),
                (
                    "Plataforma",
                    "platform",
                ),
            )
        ):
            system_layout.addWidget(
                self.create_info_card(
                    *args
                ),
                1,
                col,
            )

        layout.addWidget(
            system_box
        )

        # -----------------------------------------------------
        # ARMAZENAMENTO
        # -----------------------------------------------------

        title = QLabel(
            "Armazenamento"
        )

        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        self.storage_table = QTableWidget()

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

        # -----------------------------------------------------
        # ADAPTADORES DE REDE
        # -----------------------------------------------------

        title = QLabel(
            "Adaptadores de rede"
        )

        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(
            title
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

    def update_computer_page(self):
        data = self.data_source.get_system()

        for key in (
            "hostname",
            "current_user",
            "operating_system",
            "operating_system_release",
            "processor",
            "architecture",
            "python_version",
            "boot_time",
            "uptime",
            "platform",
        ):
            self.computer_labels[
                key
            ].setText(
                str(
                    data.get(
                        key,
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

        self.computer_labels[
            "cores"
        ].setText(
            f"{physical} físicos / "
            f"{logical} lógicos\n"
            + (
                f"{frequency:.0f} MHz"
                if frequency is not None
                else "N/D"
            )
        )

        self.computer_labels[
            "memory_total"
        ].setText(
            f'{data.get("memory_total_gb", 0):.2f} GB'
        )

        gpus = data.get(
            "gpus",
            [],
        )

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
                    f"{name} ({memory:.2f} GB)"
                )
            else:
                gpu_lines.append(
                    name
                )

        self.computer_labels[
            "gpu_summary"
        ].setText(
            "\n".join(
                gpu_lines
            )
            if gpu_lines
            else "GPU não identificada"
        )

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
                f'{partition.get("total_gb", 0):.2f} GB',
                f'{partition.get("free_gb", 0):.2f} GB',
                f'{partition.get("usage_percent", 0):.1f}%',
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
            ipv4 = ", ".join(
                adapter.get(
                    "ipv4",
                    [],
                )
            ) or "-"

            ipv6 = ", ".join(
                adapter.get(
                    "ipv6",
                    [],
                )
            ) or "-"

            speed = adapter.get(
                "speed_mbps",
                0,
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
                (
                    f"{speed} Mbps"
                    if speed
                    else "-"
                ),
                ipv4,
                ipv6,
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
    # AÇÕES DO COMPUTADOR
    # =========================================================

    def refresh_computer_action(self):
        try:
            self.update_computer_page()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível atualizar "
                "as informações do computador.\n\n"
                f"{error}",
            )

    def lock_computer_action(self):
        if QMessageBox.question(
            self,
            "Bloquear computador",
            "Deseja realmente bloquear "
            "esta estação de trabalho?\n\n"
            "O Windows será bloqueado imediatamente.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        try:
            self.control_source.lock_computer()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível bloquear "
                "o computador.\n\n"
                f"{error}",
            )

    def restart_computer_action(self):
        if QMessageBox.question(
            self,
            "Reiniciar computador",
            "ATENÇÃO!\n\n"
            "O computador será reiniciado em 30 segundos.\n\n"
            "Salve seu trabalho antes de continuar.\n\n"
            "Deseja realmente reiniciar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        try:
            self.control_source.restart_computer(
                delay_seconds=30
            )

            QMessageBox.information(
                self,
                "Reinício agendado",
                "O reinício foi agendado "
                "para daqui a 30 segundos.\n\n"
                "Se precisar cancelar, use "
                "'Cancelar desligamento'.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível agendar "
                "o reinício.\n\n"
                f"{error}",
            )

    def shutdown_computer_action(self):
        if QMessageBox.question(
            self,
            "Desligar computador",
            "ATENÇÃO!\n\n"
            "O computador será desligado em 30 segundos.\n\n"
            "Salve seu trabalho antes de continuar.\n\n"
            "Deseja realmente desligar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        try:
            self.control_source.shutdown_computer(
                delay_seconds=30
            )

            QMessageBox.information(
                self,
                "Desligamento agendado",
                "O desligamento foi agendado "
                "para daqui a 30 segundos.\n\n"
                "Se precisar cancelar, use "
                "'Cancelar desligamento'.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível agendar "
                "o desligamento.\n\n"
                f"{error}",
            )

    def cancel_shutdown_action(self):
        try:
            self.control_source.cancel_shutdown()

            QMessageBox.information(
                self,
                "SysView",
                "Desligamento ou reinício "
                "programado cancelado.",
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Nenhuma ação programada",
                "Não foi possível cancelar "
                "uma ação programada.\n\n"
                f"{error}",
            )

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
            "font-size: 36px; font-weight: bold;"
        )

        self.cpu_progress = QProgressBar()

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
        dashboard = self.data_source.get_dashboard()

        cpu = dashboard[
            "cpu"
        ]

        usage = cpu.get(
            "usage_percent",
            0,
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
            f"Núcleos físicos: "
            f"{cpu.get('physical_cores', '-')}"
            " • "
            f"Núcleos lógicos: "
            f"{cpu.get('logical_cores', '-')}"
            " • "
            f"Frequência atual: "
            f"{frequency_text}"
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
            "font-size: 36px; font-weight: bold;"
        )

        self.memory_progress = QProgressBar()

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
        dashboard = self.data_source.get_dashboard()

        memory = dashboard[
            "memory"
        ]

        usage = memory.get(
            "usage_percent",
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
            f"Usado: "
            f"{memory.get('used_gb', 0):.2f} GB"
            " • "
            f"Disponível: "
            f"{memory.get('available_gb', 0):.2f} GB"
            " • "
            f"Total: "
            f"{memory.get('total_gb', 0):.2f} GB"
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
            "font-size: 36px; font-weight: bold;"
        )

        self.disk_progress = QProgressBar()

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
        dashboard = self.data_source.get_dashboard()

        disk = dashboard[
            "disk"
        ]

        usage = disk.get(
            "usage_percent",
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
            f"Usado: "
            f"{disk.get('used_gb', 0):.2f} GB"
            " • "
            f"Livre: "
            f"{disk.get('free_gb', 0):.2f} GB"
            " • "
            f"Total: "
            f"{disk.get('total_gb', 0):.2f} GB"
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

        self.network_table = QTableWidget()

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

        # -----------------------------------------------------
        # VELOCIDADE
        # -----------------------------------------------------

        speed_layout = QGridLayout()

        upload_box = QFrame()

        upload_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        upload_box.setObjectName("sysviewPanel")

        upload_layout = QVBoxLayout(
            upload_box
        )

        upload_layout.addWidget(
            QLabel("UPLOAD")
        )

        self.network_upload_label = QLabel(
            "0 B/s"
        )

        self.network_upload_label.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        upload_layout.addWidget(
            self.network_upload_label
        )

        download_box = QFrame()

        download_box.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        download_box.setObjectName("sysviewPanel")

        download_layout = QVBoxLayout(
            download_box
        )

        download_layout.addWidget(
            QLabel("DOWNLOAD")
        )

        self.network_download_label = QLabel(
            "0 B/s"
        )

        self.network_download_label.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
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

        # -----------------------------------------------------
        # GRÁFICO
        # -----------------------------------------------------

        self.network_plot = None
        self.network_curve_upload = None
        self.network_curve_download = None
        self.network_history = []

        try:

            import pyqtgraph as pg

            self.network_plot = pg.PlotWidget()

            self.network_plot.setBackground("#151F30")
            self.network_plot.setTitle("Tráfego de rede em tempo real", color="#E2E8F0", size="12pt")
            self.network_plot.getAxis("left").setTextPen("#94A3B8")
            self.network_plot.getAxis("bottom").setTextPen("#94A3B8")

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

            self.network_curve_upload = self.network_plot.plot(
                name="Upload", pen=pg.mkPen("#38BDF8", width=2)
            )

            self.network_curve_download = self.network_plot.plot(
                name="Download", pen=pg.mkPen("#34D399", width=2)
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
        network = self.data_source.get_network()

        data = network.get(
            "interfaces",
            [],
        )

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
                f"{interface.get('speed_mbps', 0)} Mbps",
                interface.get(
                    "ipv4"
                )
                or "-",
                interface.get(
                    "ipv6"
                )
                or "-",
                interface.get(
                    "mac"
                )
                or "-",
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

        self.network_table.resizeColumnsToContents()

        self.update_network_speed(
            network.get(
                "speed",
                {},
            )
        )

    def update_network_speed(
        self,
        speed=None,
    ):
        if speed is None:
            network = self.data_source.get_network()

            speed = network.get(
                "speed",
                {},
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
            f"Upload: "
            f"{self.format_bytes(total_upload)}/s"
            " • "
            f"Download: "
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
            self.network_history.pop(0)

        if (
            self.network_curve_upload
            is not None
            and self.network_curve_download
            is not None
        ):

            self.network_curve_upload.setData(
                [
                    x[0]
                    for x in self.network_history
                ]
            )

            self.network_curve_download.setData(
                [
                    x[1]
                    for x in self.network_history
                ]
            )

    # =========================================================
    # CONEXÕES DE REDE
    # =========================================================

    def update_network_connections_page(self):
        try:

            self.network_connections_page.refresh_connections()

        except Exception as error:

            print(
                "Erro ao atualizar conexões de rede:",
                error,
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

        self.process_search = QLineEdit()

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

        self.terminate_process_button = (
            QPushButton(
                "Finalizar processo"
            )
        )

        self.setObjectName("dangerButton")

        self.terminate_process_button.clicked.connect(
            self.terminate_selected_process
        )

        controls.addWidget(
            self.process_search
        )

        controls.addWidget(
            refresh_button
        )

        controls.addWidget(
            self.terminate_process_button
        )

        layout.addLayout(
            controls
        )

        self.process_table = QTableWidget()

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

        self.process_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.process_table.setSortingEnabled(
            True
        )

        self.process_table.itemSelectionChanged.connect(
            self.update_process_details
        )

        self.process_table.horizontalHeader().sortIndicatorChanged.connect(
            self.process_sort_changed
        )

        layout.addWidget(
            self.process_table
        )

        details_title = QLabel(
            "Detalhes do processo"
        )

        details_title.setStyleSheet(
            "font-size: 17px; font-weight: bold;"
        )

        layout.addWidget(
            details_title
        )

        self.process_details = QLabel(
            "Selecione um processo para ver os detalhes."
        )

        self.process_details.setWordWrap(
            True
        )

        layout.addWidget(
            self.process_details
        )

        self.process_status = QLabel(
            "Carregando..."
        )

        layout.addWidget(
            self.process_status
        )

        return page

    def update_process_page(self):
        self.processes_data = (
            self.data_source.get_processes()
        )

        self.populate_process_table(
            self.processes_data
        )

    def force_refresh_processes(self):
        self.processes_data = (
            self.data_source.get_processes()
        )

        self.process_table_signature = None

        self.populate_process_table(
            self.processes_data,
            force_rebuild=True,
        )

    def get_filtered_processes(
        self,
        processes,
    ):
        search = (
            self.process_search.text()
            .strip()
            .lower()
        )

        if not search:
            return list(processes)

        return [
            process
            for process in processes
            if (
                search
                in str(
                    process.get(
                        "name"
                    )
                    or ""
                ).lower()
            )
            or (
                search
                in str(
                    process.get(
                        "pid"
                    )
                    or ""
                ).lower()
            )
            or (
                search
                in str(
                    process.get(
                        "username"
                    )
                    or ""
                ).lower()
            )
        ]

    def get_process_signature(
        self,
        processes,
    ):
        return tuple(
            sorted(
                int(
                    process.get(
                        "pid"
                    )
                )
                for process in processes
                if process.get(
                    "pid"
                )
                is not None
            )
        )

    def populate_process_table(
        self,
        processes,
        force_rebuild=False,
    ):
        visible = (
            self.get_filtered_processes(
                processes
            )
        )

        signature = (
            self.get_process_signature(
                visible
            )
        )

        search = (
            self.process_search.text()
            .strip()
            .lower()
        )

        search_changed = (
            search
            != self.process_search_text
        )

        self.process_search_text = search

        rebuild = (
            force_rebuild
            or search_changed
            or signature
            != self.process_table_signature
            or self.process_table.rowCount()
            != len(visible)
        )

        selected_pid = (
            self.get_selected_process_pid()
        )

        if not rebuild:

            self.update_process_rows(
                visible
            )

            if selected_pid is not None:
                self.select_process_by_pid(
                    selected_pid
                )

            self.process_status.setText(
                f"{len(visible)} processos encontrados."
            )

            return

        self.process_table.setSortingEnabled(
            False
        )

        self.process_table.setRowCount(
            len(visible)
        )

        for row, process in enumerate(
            visible
        ):
            self.set_process_row(
                row,
                process,
            )

        self.process_table_signature = (
            signature
        )

        self.process_table.resizeColumnsToContents()

        self.process_table.setSortingEnabled(
            True
        )

        if (
            self.process_sort_column
            is not None
        ):
            self.process_table.sortItems(
                self.process_sort_column,
                self.process_sort_order,
            )

        if selected_pid is not None:
            self.select_process_by_pid(
                selected_pid
            )

        self.process_status.setText(
            f"{len(visible)} processos encontrados."
        )

        self.update_process_details()

    def set_process_row(
        self,
        row,
        process,
    ):
        values = [
            process.get(
                "pid",
                "-",
            ),
            process.get(
                "name"
            )
            or "-",
            process.get(
                "username"
            )
            or "-",
            f"{process.get('cpu_percent', 0):.2f}",
            f"{process.get('memory_percent', 0):.2f}",
            process.get(
                "status"
            )
            or "-",
            process.get(
                "num_threads"
            )
            or 0,
        ]

        for column, value in enumerate(
            values
        ):

            item = QTableWidgetItem(
                str(value)
            )

            if column == 0:
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    process.get(
                        "pid"
                    ),
                )

            if column in (
                3,
                4,
            ):
                try:

                    numeric = float(
                        value
                    )

                    item.setData(
                        Qt.ItemDataRole.UserRole + 1,
                        numeric,
                    )

                    if numeric >= 80:

                        font = item.font()

                        font.setBold(
                            True
                        )

                        item.setFont(
                            font
                        )

                        item.setToolTip(
                            "Uso elevado."
                        )

                    elif numeric >= 50:

                        item.setToolTip(
                            "Uso acima do normal."
                        )

                except (
                    TypeError,
                    ValueError,
                ):
                    pass

            self.process_table.setItem(
                row,
                column,
                item,
            )

    def update_process_rows(
        self,
        processes,
    ):
        self.process_table.setSortingEnabled(
            False
        )

        row_by_pid = {}

        for row in range(
            self.process_table.rowCount()
        ):

            item = self.process_table.item(
                row,
                0,
            )

            if (
                item is not None
                and item.data(
                    Qt.ItemDataRole.UserRole
                )
                is not None
            ):

                row_by_pid[
                    int(
                        item.data(
                            Qt.ItemDataRole.UserRole
                        )
                    )
                ] = row

        for process in processes:

            pid = process.get(
                "pid"
            )

            if (
                pid is not None
                and int(pid)
                in row_by_pid
            ):

                self.set_process_row(
                    row_by_pid[
                        int(pid)
                    ],
                    process,
                )

        self.process_table.setSortingEnabled(
            True
        )

        if (
            self.process_sort_column
            is not None
        ):

            self.process_table.sortItems(
                self.process_sort_column,
                self.process_sort_order,
            )

    def process_sort_changed(
        self,
        column,
        order,
    ):
        self.process_sort_column = column
        self.process_sort_order = order

    def select_process_by_pid(
        self,
        pid,
    ):
        if pid is None:
            return

        self.process_table.blockSignals(
            True
        )

        try:

            for row in range(
                self.process_table.rowCount()
            ):

                item = self.process_table.item(
                    row,
                    0,
                )

                if (
                    item is not None
                    and item.data(
                        Qt.ItemDataRole.UserRole
                    )
                    == pid
                ):

                    self.process_table.selectRow(
                        row
                    )

                    self.process_table.setCurrentCell(
                        row,
                        0,
                    )

                    return

        finally:

            self.process_table.blockSignals(
                False
            )

        self.update_process_details()

    def filter_processes(
        self,
        _text,
    ):
        self.process_table_signature = None

        self.populate_process_table(
            self.processes_data,
            force_rebuild=True,
        )

    def get_selected_process_pid(
        self,
    ):
        row = (
            self.process_table.currentRow()
        )

        if row < 0:
            return None

        item = self.process_table.item(
            row,
            0,
        )

        if item is None:
            return None

        pid = item.data(
            Qt.ItemDataRole.UserRole
        )

        try:

            return (
                int(pid)
                if pid is not None
                else None
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    def update_process_details(self):
        pid = (
            self.get_selected_process_pid()
        )

        self.selected_process_pid = pid

        if pid is None:

            self.process_details.setText(
                "Selecione um processo "
                "para ver os detalhes."
            )

            return

        try:

            process = self.data_source.get_process(
                pid
            )

        except Exception as error:

            self.process_details.setText(
                "Erro ao consultar o processo:\n"
                f"{error}"
            )

            return

        if not process:

            self.process_details.setText(
                "O processo não está mais em execução."
            )

            return

        details = [
            f"PID: {process.get('pid', '-')}",
            f"Nome: {process.get('name') or '-'}",
            f"Usuário: {process.get('username') or '-'}",
            f"Status: {process.get('status') or '-'}",
            f"CPU: {process.get('cpu_percent', 0):.2f}%",
            f"Memória: {process.get('memory_percent', 0):.2f}%",
            f"Memória física: {process.get('memory_rss_mb', 0):.2f} MB",
            f"Threads: {process.get('num_threads') or 0}",
            f"Executável: {process.get('exe') or '-'}",
        ]

        try:

            proc = psutil.Process(
                pid
            )

            details.insert(
                3,
                f"PID pai: {proc.ppid()}",
            )

            try:

                details.append(
                    f"Criado em: "
                    f"{proc.create_time():.0f}"
                )

            except (
                psutil.AccessDenied,
                psutil.NoSuchProcess,
            ):
                pass

        except (
            psutil.AccessDenied,
            psutil.NoSuchProcess,
            psutil.ZombieProcess,
        ):
            pass

        self.process_details.setText(
            "\n".join(
                details
            )
        )

    def terminate_selected_process(
        self,
    ):
        pid = (
            self.get_selected_process_pid()
        )

        if pid is None:

            QMessageBox.warning(
                self,
                "Nenhum processo selecionado",
                "Selecione um processo antes "
                "de tentar finalizá-lo.",
            )

            return

        try:

            process = self.data_source.get_process(
                pid
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível consultar "
                "o processo.\n\n"
                f"{error}",
            )

            return

        if not process:

            QMessageBox.warning(
                self,
                "Processo não encontrado",
                "Esse processo pode ter sido encerrado.",
            )

            self.force_refresh_processes()

            return

        name = process.get(
            "name"
        ) or "Desconhecido"

        protected = {
            "system",
            "registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "winlogon.exe",
            "services.exe",
            "lsass.exe",
            "svchost.exe",
        }

        if name.lower() in protected:

            QMessageBox.warning(
                self,
                "Processo protegido",
                "O SysView não permite finalizar "
                "diretamente este processo porque "
                "ele é crítico para o Windows.\n\n"
                f"Processo: {name}\n"
                f"PID: {pid}",
            )

            return

        if QMessageBox.question(
            self,
            "Finalizar processo",
            "ATENÇÃO!\n\n"
            "Você está prestes a finalizar "
            "um processo do Windows.\n\n"
            f"Processo: {name}\n"
            f"PID: {pid}\n\n"
            "Isso pode fazer o programa perder "
            "dados não salvos.\n\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:

            return

        try:

            if not self.control_source.terminate_process(
                pid
            ):

                QMessageBox.warning(
                    self,
                    "Processo não encontrado",
                    "O processo já pode ter sido encerrado.",
                )

                self.force_refresh_processes()

                return

            QMessageBox.information(
                self,
                "Processo finalizado",
                f"O processo '{name}' "
                "recebeu a solicitação de encerramento.",
            )

            self.force_refresh_processes()

        except PermissionError as error:

            QMessageBox.critical(
                self,
                "Acesso negado",
                "O Windows não permitiu "
                "finalizar o processo.\n\n"
                "Isso normalmente acontece com "
                "processos protegidos ou que "
                "pertencem a outro nível de privilégio.\n\n"
                f"{error}",
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível finalizar "
                "o processo.\n\n"
                f"{error}",
            )

    # =========================================================
    # SERVIÇOS
    # =========================================================

    def update_services_page(self):
        services = (
            self.data_source.get_services()
        )

        self.services_page.services = (
            services
        )

        self.services_page.update_services_table()

    # =========================================================
    # UTILITÁRIOS
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

        size = float(value)

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
    # ENCERRAMENTO
    # =========================================================

    def closeEvent(
        self,
        event,
    ):
        self.timer.stop()

        event.accept()


def run_app():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    window = MainWindow()

    window.show()

    return app.exec()


if __name__ == "__main__":
    run_app()

