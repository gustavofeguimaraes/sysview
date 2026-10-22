from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.interfaces.control_source import ControlSource
from app.data.interfaces.data_source import DataSource


class ServicesPage(QWidget):
    """
    Página para visualizar e controlar serviços do Windows.

    Também apresenta a correlação:

        Serviço
           ↓
        Processo
           ↓
          Rede

    A página não acessa diretamente o monitor global.
    Toda coleta passa pela DataSource e todo controle
    passa pela ControlSource.
    """

    def __init__(
        self,
        data_source: DataSource,
        control_source: ControlSource,
    ):
        super().__init__()

        self.data_source = data_source
        self.control_source = control_source

        self.services = []
        self.filtered_services = []
        self.selected_service = None

        self.setup_widgets()
        self.setup_ui()
        self.load_services()

    def set_data_source(
        self,
        data_source: DataSource,
    ) -> None:
        self.data_source = data_source
        self.services = []
        self.filtered_services = []
        self.selected_service = None
        self.clear_details()
        self.load_services()

    def set_control_source(
        self,
        control_source: ControlSource,
    ) -> None:
        self.control_source = control_source

    def setup_widgets(self):
        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Pesquisar serviço..."
        )

        self.search_input.textChanged.connect(
            self.update_services_table
        )

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            [
                "Nome",
                "Nome de exibição",
                "Status",
                "Inicialização",
                "PID",
            ]
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.itemSelectionChanged.connect(
            self.update_details
        )

        self.refresh_button = QPushButton(
            "Atualizar"
        )

        self.start_button = QPushButton(
            "Iniciar"
        )

        self.stop_button = QPushButton(
            "Parar"
        )

        self.restart_button = QPushButton(
            "Reiniciar"
        )

        self.refresh_button.clicked.connect(
            self.load_services
        )

        self.start_button.clicked.connect(
            self.start_selected_service
        )

        self.stop_button.clicked.connect(
            self.stop_selected_service
        )

        self.restart_button.clicked.connect(
            self.restart_selected_service
        )

        self.service_details = QLabel(
            "Selecione um serviço para ver os detalhes."
        )

        self.service_details.setWordWrap(True)

        self.service_details.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.process_details = QLabel(
            "Nenhum processo associado."
        )

        self.process_details.setWordWrap(True)

        self.process_details.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.network_details = QLabel(
            "Nenhuma informação de rede disponível."
        )

        self.network_details.setWordWrap(True)

        self.network_details.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.connections_table = QTableWidget()

        self.connections_table.setColumnCount(7)

        self.connections_table.setHorizontalHeaderLabels(
            [
                "Protocolo",
                "Local",
                "Porta local",
                "Remoto",
                "Porta remota",
                "Status",
                "PID",
            ]
        )

        self.connections_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.connections_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.connections_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.connections_table.setMaximumHeight(
            220
        )

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(
            "Serviços do Windows"
        )

        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Visualize, controle e analise os serviços "
            "e os processos relacionados."
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addWidget(
            self.start_button
        )

        buttons.addWidget(
            self.stop_button
        )

        buttons.addWidget(
            self.restart_button
        )

        buttons.addStretch()

        layout.addLayout(buttons)

        service_group = QGroupBox(
            "Serviço selecionado"
        )

        service_layout = QVBoxLayout(
            service_group
        )

        service_layout.addWidget(
            self.service_details
        )

        layout.addWidget(
            service_group
        )

        process_group = QGroupBox(
            "Processo associado"
        )

        process_layout = QVBoxLayout(
            process_group
        )

        process_layout.addWidget(
            self.process_details
        )

        layout.addWidget(
            process_group
        )

        network_group = QGroupBox(
            "Rede do processo"
        )

        network_layout = QVBoxLayout(
            network_group
        )

        network_layout.addWidget(
            self.network_details
        )

        network_layout.addWidget(
            self.connections_table
        )

        layout.addWidget(
            network_group
        )

    def load_services(self):
        try:
            self.services = (
                self.data_source.get_services()
            )

            self.update_services_table()

        except PermissionError as error:
            QMessageBox.critical(
                self,
                "Acesso negado",
                (
                    "O Windows não permitiu consultar "
                    "os serviços.\n\n"
                    f"{error}"
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                (
                    "Não foi possível carregar os serviços."
                    f"\n\n{error}"
                ),
            )

    def update_services_table(self):
        search = (
            self.search_input
            .text()
            .strip()
            .lower()
        )

        filtered_services = []

        for service in self.services:
            name = service.get("name") or ""

            display_name = (
                service.get("display_name")
                or ""
            )

            if (
                search
                and search not in name.lower()
                and search not in display_name.lower()
            ):
                continue

            filtered_services.append(
                service
            )

        self.filtered_services = (
            filtered_services
        )

        current_name = (
            self.get_selected_service_name()
        )

        self.table.blockSignals(True)

        try:
            self.table.setRowCount(
                len(filtered_services)
            )

            selected_row = -1

            for row, service in enumerate(
                filtered_services
            ):
                name = service.get("name") or ""

                values = [
                    name,
                    service.get(
                        "display_name"
                    )
                    or "",
                    service.get(
                        "status"
                    )
                    or "",
                    service.get(
                        "start_type"
                    )
                    or "",
                    str(
                        service.get("pid")
                        or ""
                    ),
                ]

                for column, value in enumerate(
                    values
                ):
                    item = QTableWidgetItem(
                        value
                    )

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        name,
                    )

                    self.table.setItem(
                        row,
                        column,
                        item,
                    )

                if (
                    current_name
                    and name == current_name
                ):
                    selected_row = row

        finally:
            self.table.blockSignals(False)

        self.table.resizeColumnsToContents()

        if selected_row >= 0:
            self.table.selectRow(
                selected_row
            )

        elif self.table.rowCount() > 0:
            self.table.selectRow(0)

        else:
            self.clear_details()

    def update_service_table(self):
        self.update_services_table()

    def get_selected_service_name(
        self,
    ):
        row = self.table.currentRow()

        if row < 0:
            return None

        item = self.table.item(
            row,
            0,
        )

        if item is None:
            return None

        return item.data(
            Qt.ItemDataRole.UserRole
        )

    def get_selected_service(self):
        name = (
            self.get_selected_service_name()
        )

        if not name:
            return None

        for service in self.services:
            if service.get("name") == name:
                return service

        return None

    def update_details(self):
        service = (
            self.get_selected_service()
        )

        if not service:
            self.clear_details()
            return

        self.selected_service = service

        self.update_service_details(
            service
        )

        self.update_process_network_details(
            service
        )

    def update_service_details(
        self,
        service: dict,
    ):
        details = [
            (
                f"Nome: "
                f"{service.get('name') or '-'}"
            ),
            (
                "Nome de exibição: "
                f"{service.get('display_name') or '-'}"
            ),
            (
                f"Status: "
                f"{service.get('status') or '-'}"
            ),
            (
                "Inicialização: "
                f"{service.get('start_type') or '-'}"
            ),
            (
                f"PID: "
                f"{service.get('pid') or '-'}"
            ),
            (
                f"Usuário: "
                f"{service.get('username') or '-'}"
            ),
            (
                "Executável: "
                f"{service.get('binpath') or '-'}"
            ),
            (
                "Descrição: "
                f"{service.get('description') or '-'}"
            ),
        ]

        self.service_details.setText(
            "\n".join(details)
        )

    def update_process_network_details(
        self,
        service: dict,
    ):
        try:
            data = (
                self.data_source
                .get_service_process_network(
                    service
                )
            )

        except PermissionError as error:
            self.process_details.setText(
                "Acesso negado ao consultar "
                "as informações do processo.\n\n"
                f"{error}"
            )

            self.network_details.setText(
                "As conexões de rede não puderam "
                "ser consultadas."
            )

            self.connections_table.setRowCount(
                0
            )

            return

        except NotImplementedError as error:
            self.process_details.setText(
                "A consulta do processo associado "
                "ainda não está disponível para "
                "esta fonte de dados.\n\n"
                f"{error}"
            )

            self.network_details.setText(
                "A consulta de rede deste processo "
                "ainda não está disponível."
            )

            self.connections_table.setRowCount(
                0
            )

            return

        except Exception as error:
            self.process_details.setText(
                "Erro ao consultar o processo:\n\n"
                f"{error}"
            )

            self.network_details.setText(
                "Erro ao consultar as informações "
                "de rede."
            )

            self.connections_table.setRowCount(
                0
            )

            return

        process = data.get(
            "process"
        )

        network = (
            data.get("network")
            or {}
        )

        connections = (
            data.get("connections")
            or []
        )

        self.update_process_details(
            process
        )

        self.update_network_details(
            network
        )

        self.update_connections_table(
            connections
        )

    def update_process_details(
        self,
        process: dict | None,
    ):
        if not process:
            self.process_details.setText(
                "Nenhum processo associado "
                "a este serviço."
            )

            return

        details = [
            (
                f"Nome: "
                f"{process.get('name') or '-'}"
            ),
            (
                f"PID: "
                f"{process.get('pid') or '-'}"
            ),
            (
                "Usuário: "
                f"{process.get('username') or '-'}"
            ),
            (
                f"Status: "
                f"{process.get('status') or '-'}"
            ),
            (
                "CPU: "
                f"{process.get('cpu_percent', 0):.2f}%"
            ),
            (
                "Memória: "
                f"{process.get('memory_rss_mb', 0):.2f} MB"
            ),
            (
                "Memória (%): "
                f"{process.get('memory_percent', 0):.2f}%"
            ),
            (
                "Threads: "
                f"{process.get('num_threads') or '-'}"
            ),
            (
                "PID pai: "
                f"{process.get('ppid') or '-'}"
            ),
            (
                "Executável: "
                f"{process.get('exe') or '-'}"
            ),
        ]

        self.process_details.setText(
            "\n".join(details)
        )

    def update_network_details(
        self,
        network: dict,
    ):
        local_ports = (
            network.get("local_ports")
            or []
        )

        remote_addresses = (
            network.get("remote_addresses")
            or []
        )

        local_ports_text = (
            ", ".join(
                str(port)
                for port in local_ports
            )
            if local_ports
            else "-"
        )

        remote_addresses_text = (
            ", ".join(
                str(address)
                for address in remote_addresses
            )
            if remote_addresses
            else "-"
        )

        details = [
            (
                "Total de conexões: "
                f"{network.get('total_connections', 0)}"
            ),
            (
                "TCP: "
                f"{network.get('tcp_connections', 0)}"
            ),
            (
                "UDP: "
                f"{network.get('udp_connections', 0)}"
            ),
            (
                "LISTEN: "
                f"{network.get('listening', 0)}"
            ),
            (
                "ESTABLISHED: "
                f"{network.get('established', 0)}"
            ),
            (
                "Portas locais: "
                f"{local_ports_text}"
            ),
            (
                "Endereços remotos: "
                f"{remote_addresses_text}"
            ),
        ]

        self.network_details.setText(
            "\n".join(details)
        )

    def update_connections_table(
        self,
        connections: list[dict],
    ):
        self.connections_table.setRowCount(
            len(connections)
        )

        for row, connection in enumerate(
            connections
        ):
            local_address = (
                connection.get(
                    "local_address"
                )
                or "-"
            )

            local_port = (
                connection.get(
                    "local_port"
                )
                or "-"
            )

            remote_address = (
                connection.get(
                    "remote_address"
                )
                or "-"
            )

            remote_port = (
                connection.get(
                    "remote_port"
                )
                or "-"
            )

            values = [
                connection.get(
                    "protocol"
                )
                or "-",
                str(local_address),
                str(local_port),
                str(remote_address),
                str(remote_port),
                connection.get(
                    "status"
                )
                or "-",
                str(
                    connection.get(
                        "pid"
                    )
                    or "-"
                ),
            ]

            for column, value in enumerate(
                values
            ):
                self.connections_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        value
                    ),
                )

        self.connections_table.resizeColumnsToContents()

    def clear_details(self):
        self.selected_service = None

        self.service_details.setText(
            "Selecione um serviço para ver os detalhes."
        )

        self.process_details.setText(
            "Nenhum processo associado."
        )

        self.network_details.setText(
            "Nenhuma informação de rede disponível."
        )

        self.connections_table.setRowCount(
            0
        )

    def start_selected_service(self):
        self._execute_service_action(
            "iniciar",
            self.control_source.start_service,
        )

    def stop_selected_service(self):
        self._execute_service_action(
            "parar",
            self.control_source.stop_service,
        )

    def restart_selected_service(self):
        self._execute_service_action(
            "reiniciar",
            self.control_source.restart_service,
        )

    def _execute_service_action(
        self,
        action_name,
        action,
    ):
        name = (
            self.get_selected_service_name()
        )

        if not name:
            QMessageBox.warning(
                self,
                "Nenhum serviço selecionado",
                "Selecione um serviço primeiro.",
            )

            return

        confirmation = QMessageBox.question(
            self,
            "Confirmar ação",
            (
                f"Deseja realmente "
                f"{action_name} o serviço:\n\n"
                f"{name}?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            confirmation
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            action(name)

            QMessageBox.information(
                self,
                "Sucesso",
                (
                    f"Serviço {action_name}"
                    "do com sucesso."
                ),
            )

            self.load_services()

        except PermissionError as error:
            QMessageBox.critical(
                self,
                "Acesso negado",
                (
                    "O Windows não permitiu "
                    f"{action_name} o serviço.\n\n"
                    f"{error}"
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                (
                    f"Não foi possível "
                    f"{action_name} o serviço."
                    f"\n\n{error}"
                ),
            )