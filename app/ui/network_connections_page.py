
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.interfaces.data_source import DataSource


class NetworkConnectionsPage(QWidget):
    """
    Página de monitoramento das conexões de rede.

    A página não acessa diretamente o monitor global
    nem os serviços do sistema.

    Toda coleta é feita através da DataSource, permitindo
    trabalhar futuramente com computadores locais,
    Windows remotos e outros dispositivos.
    """

    def __init__(
        self,
        data_source: DataSource,
        parent=None,
    ):
        super().__init__(parent)

        self.data_source = data_source

        self.connections = []

        self._build_ui()


    # =========================================================
    # FONTE DE DADOS
    # =========================================================

    def set_data_source(
        self,
        data_source: DataSource,
    ) -> None:
        """
        Troca a fonte de dados da página.

        Permite mudar entre computador local e remoto
        sem precisar recriar a página.
        """

        self.data_source = data_source

        self.connections = []

        self.clear_details()

        self.refresh_connections()

    # =========================================================
    # INTERFACE
    # =========================================================

    def _build_ui(self):
        main_layout = QVBoxLayout(
            self
        )

        # -----------------------------------------------------
        # TÍTULO
        # -----------------------------------------------------

        title = QLabel(
            "Conexões de Rede"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
            }
            """
        )

        subtitle = QLabel(
            "Monitoramento de conexões TCP e UDP "
            "abertas no dispositivo."
        )

        main_layout.addWidget(
            title
        )

        main_layout.addWidget(
            subtitle
        )

        # -----------------------------------------------------
        # CONTROLES
        # -----------------------------------------------------

        controls = QHBoxLayout()

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Pesquisar IP, porta, processo, PID..."
        )

        self.search_input.textChanged.connect(
            self.update_table
        )

        self.protocol_filter = QComboBox()

        self.protocol_filter.addItems(
            [
                "Todos",
                "TCP",
                "UDP",
            ]
        )

        self.protocol_filter.currentTextChanged.connect(
            self.update_table
        )

        self.status_filter = QComboBox()

        self.status_filter.addItems(
            [
                "Todos",
                "LISTEN",
                "ESTABLISHED",
                "TIME_WAIT",
                "CLOSE_WAIT",
                "NONE",
            ]
        )

        self.status_filter.currentTextChanged.connect(
            self.update_table
        )

        self.refresh_button = QPushButton(
            "Atualizar"
        )

        self.refresh_button.clicked.connect(
            self.refresh_connections
        )

        controls.addWidget(
            self.search_input
        )

        controls.addWidget(
            self.protocol_filter
        )

        controls.addWidget(
            self.status_filter
        )

        controls.addWidget(
            self.refresh_button
        )

        main_layout.addLayout(
            controls
        )

        # -----------------------------------------------------
        # SPLITTER
        # -----------------------------------------------------

        splitter = QSplitter(
            Qt.Orientation.Vertical
        )

        # -----------------------------------------------------
        # TABELA
        # -----------------------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(
            9
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Protocolo",
                "Endereço local",
                "Porta local",
                "Endereço remoto",
                "Porta remota",
                "Estado",
                "PID",
                "Processo",
                "Usuário",
            ]
        )

        self.table.setSortingEnabled(
            True
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.itemSelectionChanged.connect(
            self.show_selected_connection
        )

        header = self.table.horizontalHeader()

        for column in range(
            9
        ):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Interactive,
            )

        header.setStretchLastSection(
            True
        )

        splitter.addWidget(
            self.table
        )

        # -----------------------------------------------------
        # DETALHES
        # -----------------------------------------------------

        details_box = QGroupBox(
            "Detalhes da conexão"
        )

        details_layout = QFormLayout(
            details_box
        )

        self.detail_protocol = QLabel(
            "-"
        )

        self.detail_local = QLabel(
            "-"
        )

        self.detail_remote = QLabel(
            "-"
        )

        self.detail_status = QLabel(
            "-"
        )

        self.detail_pid = QLabel(
            "-"
        )

        self.detail_process = QLabel(
            "-"
        )

        self.detail_username = QLabel(
            "-"
        )

        self.detail_ppid = QLabel(
            "-"
        )

        self.detail_exe = QLabel(
            "-"
        )

        self.detail_exe.setWordWrap(
            True
        )

        details_layout.addRow(
            "Protocolo:",
            self.detail_protocol,
        )

        details_layout.addRow(
            "Local:",
            self.detail_local,
        )

        details_layout.addRow(
            "Remoto:",
            self.detail_remote,
        )

        details_layout.addRow(
            "Estado:",
            self.detail_status,
        )

        details_layout.addRow(
            "PID:",
            self.detail_pid,
        )

        details_layout.addRow(
            "Processo:",
            self.detail_process,
        )

        details_layout.addRow(
            "Usuário:",
            self.detail_username,
        )

        details_layout.addRow(
            "PPID:",
            self.detail_ppid,
        )

        details_layout.addRow(
            "Executável:",
            self.detail_exe,
        )

        splitter.addWidget(
            details_box
        )

        splitter.setSizes(
            [
                500,
                220,
            ]
        )

        main_layout.addWidget(
            splitter
        )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        self.status_label = QLabel(
            "0 conexões"
        )

        main_layout.addWidget(
            self.status_label
        )

    # =========================================================
    # ATUALIZAÇÃO
    # =========================================================

    def refresh_connections(self):
        """
        Obtém as conexões através da DataSource.
        """

        try:
            self.connections = (
                self.data_source.get_network_connections()
            )

        except PermissionError as error:

            self.connections = []

            self.status_label.setText(
                f"Erro de permissão: {error}"
            )

            self.update_table()

            return

        except Exception as error:

            self.connections = []

            self.status_label.setText(
                f"Erro ao obter conexões: {error}"
            )

            self.update_table()

            return

        self.update_table()

    # =========================================================
    # FILTROS / TABELA
    # =========================================================

    def update_table(self):
        search = (
            self.search_input.text()
            .strip()
            .lower()
        )

        protocol = (
            self.protocol_filter.currentText()
        )

        status = (
            self.status_filter.currentText()
        )

        filtered = []

        for connection in self.connections:

            if (
                protocol != "Todos"
                and connection.get(
                    "protocol"
                )
                != protocol
            ):
                continue

            if (
                status != "Todos"
                and connection.get(
                    "status"
                )
                != status
            ):
                continue

            searchable = " ".join(
                [
                    str(
                        connection.get(
                            "protocol",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "local_address",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "local_port",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "remote_address",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "remote_port",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "status",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "pid",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "process",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "username",
                            "",
                        )
                    ),
                    str(
                        connection.get(
                            "exe",
                            "",
                        )
                    ),
                ]
            ).lower()

            if (
                search
                and search not in searchable
            ):
                continue

            filtered.append(
                connection
            )

        self.table.setSortingEnabled(
            False
        )

        self.table.setRowCount(
            len(filtered)
        )

        for row, connection in enumerate(
            filtered
        ):

            values = [
                connection.get(
                    "protocol"
                ),
                connection.get(
                    "local_address"
                ),
                connection.get(
                    "local_port"
                ),
                connection.get(
                    "remote_address"
                ),
                connection.get(
                    "remote_port"
                ),
                connection.get(
                    "status"
                ),
                connection.get(
                    "pid"
                ),
                connection.get(
                    "process"
                ),
                connection.get(
                    "username"
                ),
            ]

            for column, value in enumerate(
                values
            ):

                text = (
                    str(value)
                    if value is not None
                    else "-"
                )

                item = QTableWidgetItem(
                    text
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    connection,
                )

                self.table.setItem(
                    row,
                    column,
                    item,
                )

        self.table.setSortingEnabled(
            True
        )

        self.status_label.setText(
            f"{len(filtered)} conexão(ões)"
        )

    # =========================================================
    # DETALHES
    # =========================================================

    def show_selected_connection(self):
        selected_rows = (
            self.table.selectionModel()
            .selectedRows()
        )

        if not selected_rows:

            self.clear_details()

            return

        row = selected_rows[
            0
        ].row()

        item = self.table.item(
            row,
            0,
        )

        if item is None:

            self.clear_details()

            return

        connection = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            connection,
            dict,
        ):

            self.clear_details()

            return

        protocol = connection.get(
            "protocol"
        )

        local_address = connection.get(
            "local_address"
        )

        local_port = connection.get(
            "local_port"
        )

        remote_address = connection.get(
            "remote_address"
        )

        remote_port = connection.get(
            "remote_port"
        )

        self.detail_protocol.setText(
            str(
                protocol
                or "-"
            )
        )

        self.detail_local.setText(
            f"{local_address or '-'}:"
            f"{local_port or '-'}"
        )

        self.detail_remote.setText(
            f"{remote_address or '-'}:"
            f"{remote_port or '-'}"
        )

        self.detail_status.setText(
            str(
                connection.get(
                    "status"
                )
                or "-"
            )
        )

        self.detail_pid.setText(
            str(
                connection.get(
                    "pid"
                )
                or "-"
            )
        )

        self.detail_process.setText(
            str(
                connection.get(
                    "process"
                )
                or "-"
            )
        )

        self.detail_username.setText(
            str(
                connection.get(
                    "username"
                )
                or "-"
            )
        )

        self.detail_ppid.setText(
            str(
                connection.get(
                    "ppid"
                )
                or "-"
            )
        )

        self.detail_exe.setText(
            str(
                connection.get(
                    "exe"
                )
                or "-"
            )
        )

    def clear_details(self):
        self.detail_protocol.setText(
            "-"
        )

        self.detail_local.setText(
            "-"
        )

        self.detail_remote.setText(
            "-"
        )

        self.detail_status.setText(
            "-"
        )

        self.detail_pid.setText(
            "-"
        )

        self.detail_process.setText(
            "-"
        )

        self.detail_username.setText(
            "-"
        )

        self.detail_ppid.setText(
            "-"
        )

        self.detail_exe.setText(
            "-"
        )

