
import logging

import psutil
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


logger = logging.getLogger(__name__)

ACCESS_ERRORS = (
    PermissionError,
    psutil.AccessDenied,
)


class ServicesPage(QWidget):
    """
    Página de gerenciamento de serviços do Windows.

    Permite:
    - Listar e pesquisar serviços.
    - Consultar informações dos serviços.
    - Visualizar processos associados.
    - Consultar conexões de rede.
    - Iniciar, parar e reiniciar serviços autorizados.

    A coleta utiliza DataSource.
    O controle utiliza ControlSource.
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

    @staticmethod
    def _text(value, default="-"):
        if value is None or value == "":
            return default
        return str(value)

    @staticmethod
    def _number(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        table.setAlternatingRowColors(True)

        return table

    def _create_detail_label(self, placeholder):
        label = QLabel(placeholder)
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        return label

    def setup_widgets(self):
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Pesquisar serviço pelo nome..."
        )
        self.search_input.textChanged.connect(
            self.update_services_table
        )

        self.table = self._create_table([
            "Nome",
            "Nome de exibição",
            "Status",
            "Inicialização",
            "PID",
        ])

        self.table.itemSelectionChanged.connect(
            self.update_details
        )

        self.refresh_button = QPushButton("Atualizar")
        self.start_button = QPushButton("Iniciar")
        self.stop_button = QPushButton("Parar")
        self.restart_button = QPushButton("Reiniciar")

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

        self.service_details = self._create_detail_label(
            "Selecione um serviço para ver os detalhes."
        )
        self.process_details = self._create_detail_label(
            "Nenhum processo associado."
        )
        self.network_details = self._create_detail_label(
            "Nenhuma informação de rede disponível."
        )

        self.connections_table = self._create_table([
            "Protocolo",
            "Local",
            "Porta local",
            "Remoto",
            "Porta remota",
            "Status",
            "PID",
        ])
        self.connections_table.setMaximumHeight(220)

        self._update_action_buttons()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Serviços do Windows")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Visualize, controle e analise serviços, "
            "processos e conexões de rede."
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.start_button)
        buttons.addWidget(self.stop_button)
        buttons.addWidget(self.restart_button)
        buttons.addStretch()

        layout.addLayout(buttons)

        service_group = QGroupBox("Serviço selecionado")
        service_layout = QVBoxLayout(service_group)
        service_layout.addWidget(self.service_details)
        layout.addWidget(service_group)

        process_group = QGroupBox("Processo associado")
        process_layout = QVBoxLayout(process_group)
        process_layout.addWidget(self.process_details)
        layout.addWidget(process_group)

        network_group = QGroupBox("Rede do processo")
        network_layout = QVBoxLayout(network_group)
        network_layout.addWidget(self.network_details)
        network_layout.addWidget(self.connections_table)
        layout.addWidget(network_group)

    def load_services(self):
        selected_name = self.get_selected_service_name()

        try:
            services = self.data_source.get_services()
            self.services = list(services or [])

            self.update_services_table(
                preferred_name=selected_name
            )

        except ACCESS_ERRORS as error:
            logger.warning(
                "Acesso negado ao listar serviços: %s",
                error,
            )
            QMessageBox.warning(
                self,
                "Acesso negado",
                "O Windows não permitiu consultar "
                f"todos os serviços.\n\n{error}",
            )

        except Exception as error:
            logger.exception(
                "Erro ao carregar serviços"
            )
            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível carregar os serviços."
                f"\n\n{error}",
            )

    def update_services_table(self, preferred_name=None):
        search = self.search_input.text().strip().lower()

        current_name = (
            preferred_name
            if preferred_name is not None
            else self.get_selected_service_name()
        )

        self.filtered_services = [
            service
            for service in self.services
            if not search
            or search in str(
                service.get("name") or ""
            ).lower()
            or search in str(
                service.get("display_name") or ""
            ).lower()
        ]

        self.table.blockSignals(True)

        try:
            self.table.setRowCount(
                len(self.filtered_services)
            )

            selected_row = -1

            for row, service in enumerate(
                self.filtered_services
            ):
                name = str(service.get("name") or "")

                values = [
                    name,
                    self._text(
                        service.get("display_name"), ""
                    ),
                    self._text(
                        service.get("status"), ""
                    ),
                    self._text(
                        service.get("start_type"), ""
                    ),
                    self._text(
                        service.get("pid"), ""
                    ),
                ]

                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        name,
                    )
                    self.table.setItem(
                        row, column, item
                    )

                if name == current_name:
                    selected_row = row

            self.table.clearSelection()

            if selected_row >= 0:
                self.table.selectRow(selected_row)
            elif self.table.rowCount() > 0:
                self.table.selectRow(0)

        finally:
            self.table.blockSignals(False)

        self.table.resizeColumnsToContents()
        self.update_details()

    def update_service_table(self):
        """Compatibilidade com chamadas existentes."""
        self.update_services_table()

    def get_selected_service_name(self):
        row = self.table.currentRow()

        if row < 0:
            return None

        item = self.table.item(row, 0)

        if item is None or not item.isSelected():
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    def get_selected_service(self):
        name = self.get_selected_service_name()

        if not name:
            return None

        for service in self.services:
            if service.get("name") == name:
                return service

        return None

    def _update_action_buttons(self):
        service = self.get_selected_service()
        has_service = service is not None

        status = (
            str(service.get("status") or "").lower()
            if service
            else ""
        )

        start_type = (
            str(service.get("start_type") or "").lower()
            if service
            else ""
        )

        running = status == "running"
        stopped = status == "stopped"
        disabled = start_type == "disabled"

        self.start_button.setEnabled(
            has_service and stopped and not disabled
        )
        self.stop_button.setEnabled(
            has_service and running
        )
        self.restart_button.setEnabled(
            has_service and running
        )

    def update_details(self):
        service = self.get_selected_service()

        if not service:
            self.clear_details()
            return

        self.selected_service = service

        self.update_service_details(service)
        self.update_process_network_details(service)
        self._update_action_buttons()

    def update_service_details(self, service: dict):
        fields = [
            ("Nome", "name"),
            ("Nome de exibição", "display_name"),
            ("Status", "status"),
            ("Inicialização", "start_type"),
            ("PID", "pid"),
            ("Usuário", "username"),
            ("Executável", "binpath"),
            ("Descrição", "description"),
        ]

        details = [
            f"{label}: {self._text(service.get(key))}"
            for label, key in fields
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
                .get_service_process_network(service)
            ) or {}

        except ACCESS_ERRORS as error:
            self.process_details.setText(
                "Acesso negado ao consultar o processo."
                f"\n\n{error}"
            )
            self.network_details.setText(
                "As conexões de rede não puderam "
                "ser consultadas."
            )
            self.connections_table.setRowCount(0)
            return

        except NotImplementedError:
            self.process_details.setText(
                "Consulta de processo não disponível "
                "para esta fonte de dados."
            )
            self.network_details.setText(
                "Consulta de rede não disponível."
            )
            self.connections_table.setRowCount(0)
            return

        except Exception as error:
            logger.exception(
                "Erro ao consultar processo e rede"
            )
            self.process_details.setText(
                f"Erro ao consultar o processo:\n{error}"
            )
            self.network_details.setText(
                "Erro ao consultar informações de rede."
            )
            self.connections_table.setRowCount(0)
            return

        self.update_process_details(
            data.get("process")
        )
        self.update_network_details(
            data.get("network") or {}
        )
        self.update_connections_table(
            data.get("connections") or []
        )

    def update_process_details(
        self,
        process: dict | None,
    ):
        if not process:
            self.process_details.setText(
                "Nenhum processo associado a este serviço."
            )
            return

        details = [
            f"Nome: {self._text(process.get('name'))}",
            f"PID: {self._text(process.get('pid'))}",
            f"Usuário: {self._text(process.get('username'))}",
            f"Status: {self._text(process.get('status'))}",
            (
                "CPU: "
                f"{self._number(process.get('cpu_percent')):.2f}%"
            ),
            (
                "Memória: "
                f"{self._number(process.get('memory_rss_mb')):.2f} MB"
            ),
            (
                "Memória (%): "
                f"{self._number(process.get('memory_percent')):.2f}%"
            ),
            f"Threads: {self._text(process.get('num_threads'))}",
            f"PID pai: {self._text(process.get('ppid'))}",
            f"Executável: {self._text(process.get('exe'))}",
        ]

        self.process_details.setText(
            "\n".join(details)
        )

    def update_network_details(self, network: dict):
        local_ports = network.get("local_ports") or []
        remote_addresses = (
            network.get("remote_addresses") or []
        )

        local_ports_text = (
            ", ".join(map(str, local_ports))
            if local_ports else "-"
        )

        remote_addresses_text = (
            ", ".join(map(str, remote_addresses))
            if remote_addresses else "-"
        )

        fields = [
            ("Total de conexões", "total_connections"),
            ("TCP", "tcp_connections"),
            ("UDP", "udp_connections"),
            ("LISTEN", "listening"),
            ("ESTABLISHED", "established"),
        ]

        details = [
            f"{label}: {network.get(key, 0)}"
            for label, key in fields
        ]

        details.extend([
            f"Portas locais: {local_ports_text}",
            f"Endereços remotos: {remote_addresses_text}",
        ])

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

        keys = [
            "protocol",
            "local_address",
            "local_port",
            "remote_address",
            "remote_port",
            "status",
            "pid",
        ]

        for row, connection in enumerate(connections):
            for column, key in enumerate(keys):
                value = self._text(
                    connection.get(key)
                )
                self.connections_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value),
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
        self.connections_table.setRowCount(0)

        self._update_action_buttons()

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
        service = self.get_selected_service()

        if not service:
            QMessageBox.warning(
                self,
                "Nenhum serviço selecionado",
                "Selecione um serviço primeiro.",
            )
            return

        name = service.get("name")

        confirmation = QMessageBox.question(
            self,
            "Confirmar ação",
            (
                f"Deseja realmente {action_name} "
                f"o serviço:\n\n{name}?\n\n"
                "Esta operação pode afetar outros "
                "programas e recursos do Windows."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        buttons = [
            self.refresh_button,
            self.start_button,
            self.stop_button,
            self.restart_button,
        ]

        for button in buttons:
            button.setEnabled(False)

        try:
            result = action(name)

            if result is False:
                raise RuntimeError(
                    "A fonte de controle informou "
                    "que a operação não foi concluída."
                )

            messages = {
                "iniciar": "iniciado",
                "parar": "parado",
                "reiniciar": "reiniciado",
            }

            QMessageBox.information(
                self,
                "Comando executado",
                (
                    f"Comando para {action_name} o serviço "
                    f"'{name}' enviado sem erro.\n\n"
                    "Atualize a lista para conferir "
                    "o estado do serviço."
                ),
            )

            logger.info(
                "Comando %s executado para %s",
                action_name,
                name,
            )

            self.load_services()

        except ACCESS_ERRORS as error:
            logger.warning(
                "Acesso negado ao %s serviço %s: %s",
                action_name,
                name,
                error,
            )

            QMessageBox.warning(
                self,
                "Permissão necessária",
                (
                    f"O Windows não permitiu {action_name} "
                    f"o serviço '{name}'.\n\n"
                    "Esta operação pode exigir "
                    "permissões administrativas.\n\n"
                    f"Detalhes: {error}"
                ),
            )

        except (
            psutil.NoSuchProcess,
            FileNotFoundError,
        ) as error:
            QMessageBox.warning(
                self,
                "Serviço indisponível",
                (
                    "O serviço não foi encontrado "
                    "ou deixou de estar disponível."
                    f"\n\n{error}"
                ),
            )

        except Exception as error:
            logger.exception(
                "Falha ao %s serviço %s",
                action_name,
                name,
            )

            QMessageBox.critical(
                self,
                "Erro na operação",
                (
                    f"Não foi possível {action_name} "
                    f"o serviço '{name}'.\n\n{error}"
                ),
            )

        finally:
            self._update_action_buttons()
            self.refresh_button.setEnabled(True)
