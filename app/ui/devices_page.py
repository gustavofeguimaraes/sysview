"""Cadastro de dispositivos do SysView, com operações MySQL assíncronas."""

import logging
import uuid

from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,
)

from app.data.database.device_repository import DeviceRepository
from app.data.models.connection_type import ConnectionType
from app.data.models.device import Device
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType

logger = logging.getLogger(__name__)


class DeviceDialog(QDialog):
    def __init__(self, parent=None, device=None):
        super().__init__(parent)
        self.setWindowTitle("Editar dispositivo" if device else "Cadastrar dispositivo")
        self.setMinimumWidth(410)
        layout = QFormLayout(self)
        self.name = QLineEdit(device.name if device else "")
        self.name.setMaxLength(150)
        self.address = QLineEdit(device.address or "" if device else "")
        self.address.setMaxLength(255)
        self.address.setPlaceholderText("IP ou nome DNS")
        self.port = QLineEdit(str(device.port or 8765) if device else "8765")
        self.platform = QComboBox()
        self.platform.addItem("Windows", PlatformType.WINDOWS)
        self.platform.addItem("Android (futuro)", PlatformType.ANDROID)
        self.kind = QComboBox()
        for label, value in (("Computador", DeviceType.COMPUTER),
                             ("Servidor", DeviceType.SERVER),
                             ("Celular", DeviceType.MOBILE),
                             ("Equipamento de rede", DeviceType.NETWORK_DEVICE),
                             ("IoT", DeviceType.IOT)):
            self.kind.addItem(label, value)
        if device:
            self.platform.setCurrentIndex(self.platform.findData(device.platform))
            self.kind.setCurrentIndex(self.kind.findData(device.device_type))
        layout.addRow("Nome:", self.name)
        layout.addRow("Plataforma:", self.platform)
        layout.addRow("Tipo:", self.kind)
        layout.addRow("Endereço:", self.address)
        layout.addRow("Porta do agente:", self.port)
        self.hint = QLabel("O cadastro não inicia conexão nem habilita controle remoto.")
        self.hint.setWordWrap(True)
        layout.addRow(self.hint)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.original = device

    def _validate(self):
        if not self.name.text().strip() or not self.address.text().strip():
            QMessageBox.warning(self, "Dados incompletos", "Informe nome e endereço do dispositivo.")
            return
        try:
            port = int(self.port.text().strip())
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Porta inválida", "Informe uma porta entre 1 e 65535.")
            return
        self.accept()

    def get_device(self):
        old = self.original
        return Device(
            device_id=old.device_id if old else str(uuid.uuid4()),
            name=self.name.text().strip(),
            device_type=self.kind.currentData(),
            platform=self.platform.currentData(),
            connection_type=ConnectionType.REMOTE,
            address=self.address.text().strip(),
            port=int(self.port.text().strip()),
            online=old.online if old else False,
            metadata=dict(old.metadata) if old else {},
            last_seen=old.last_seen if old else None,
        )


class _DatabaseWorker(QObject):
    finished = Signal(object, object)

    def __init__(self, operation, argument=None):
        super().__init__()
        self.operation = operation
        self.argument = argument

    def run(self):
        try:
            if self.operation == "list":
                result = DeviceRepository.get_all()
            elif self.operation == "create":
                result = DeviceRepository.create(self.argument)
            elif self.operation == "update":
                result = DeviceRepository.update(self.argument)
            elif self.operation == "delete":
                result = DeviceRepository.delete(self.argument)
            else:
                raise ValueError("Operação desconhecida")
            if self.operation != "list" and not result:
                raise RuntimeError("O banco não confirmou a operação.")
            self.finished.emit(result, None)
        except Exception as exc:
            logger.exception("Falha no banco de dispositivos")
            self.finished.emit(None, str(exc))


class DevicesPage(QWidget):
    """Gerencia dispositivos remotos; selecionar não ativa monitoramento."""

    target_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = []
        self.selected_target_id = None
        self._thread = None
        self._worker = None
        self._busy = False
        self._pending_refresh = False
        layout = QVBoxLayout(self)
        heading = QLabel("Dispositivos")
        heading.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(heading)
        layout.addWidget(QLabel("Cadastre e organize computadores remotos no MySQL."))
        controls = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar lista")
        self.add_button = QPushButton("Adicionar")
        self.edit_button = QPushButton("Editar")
        self.delete_button = QPushButton("Excluir")
        self.select_button = QPushButton("Selecionar alvo")
        self.local_button = QPushButton("Voltar ao local")
        self.delete_button.setObjectName("dangerButton")
        for button in (self.refresh_button, self.add_button, self.edit_button, self.delete_button,
                       self.select_button, self.local_button):
            controls.addWidget(button)
        controls.addStretch()
        layout.addLayout(controls)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(("Nome", "Plataforma", "Tipo", "Endereço", "Porta", "Estado salvo"))
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.target_status = QLabel("Alvo selecionado: Computador local (monitoramento ativo)")
        layout.addWidget(self.target_status)
        self.status = QLabel("Aguardando carregamento...")
        layout.addWidget(self.status)
        self.refresh_button.clicked.connect(self.refresh)
        self.add_button.clicked.connect(self.add_device)
        self.edit_button.clicked.connect(self.edit_device)
        self.delete_button.clicked.connect(self.delete_device)
        self.select_button.clicked.connect(self.select_target)
        self.local_button.clicked.connect(self.select_local)
        self.table.itemSelectionChanged.connect(self._update_buttons)
        self._update_buttons()

    def _update_buttons(self):
        selected = self._selected() is not None
        self.refresh_button.setEnabled(not self._busy)
        self.add_button.setEnabled(not self._busy)
        self.edit_button.setEnabled(selected and not self._busy)
        self.delete_button.setEnabled(selected and not self._busy)
        self.select_button.setEnabled(selected and not self._busy)
        self.local_button.setEnabled(self.selected_target_id is not None and not self._busy)

    def _selected(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        device_id = item.data(Qt.ItemDataRole.UserRole)
        return next((device for device in self.devices if device.device_id == device_id), None)

    def _start(self, operation, argument=None):
        if self._busy:
            return
        self._busy = True
        self.status.setText("Consultando MySQL...")
        self._update_buttons()
        thread = QThread(self)
        worker = _DatabaseWorker(operation, argument)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(lambda result, error: self._done(operation, result, error))
        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_thread)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _clear_thread(self):
        self._thread = None
        self._worker = None
        if self._pending_refresh:
            self._pending_refresh = False
            self.refresh()

    def _done(self, operation, result, error):
        self._busy = False
        self._update_buttons()
        if error:
            self.status.setText("Falha na operação com o banco.")
            QMessageBox.warning(self, "Erro no MySQL", error)
            return
        if operation == "list":
            self.devices = result
            if self.selected_target_id is not None:
                current = next((d for d in result if d.device_id == self.selected_target_id), None)
                if current is None:
                    self.select_local()
                else:
                    self._display_target(current)
            self.table.setRowCount(len(result))
            for row, device in enumerate(result):
                values = (device.name, device.platform.value, device.device_type.value,
                          device.address or "-", str(device.port or "-"),
                          "Online (último registro)" if device.online else "Offline (último registro)")
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, device.device_id)
                    self.table.setItem(row, column, item)
            self.status.setText(f"{len(result)} dispositivo(s) cadastrado(s). Estado salvo não é verificação em tempo real.")
            self._update_buttons()
        else:
            self.status.setText("Operação concluída. Atualizando lista...")
            self._pending_refresh = True

    def refresh(self):
        self._start("list")

    def add_device(self):
        dialog = DeviceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._start("create", dialog.get_device())

    def edit_device(self):
        device = self._selected()
        if device is None:
            return
        dialog = DeviceDialog(self, device)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._start("update", dialog.get_device())

    def delete_device(self):
        device = self._selected()
        if device is None:
            return
        answer = QMessageBox.question(self, "Excluir dispositivo",
                                      f"Excluir '{device.name}' do MySQL?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self._start("delete", device.device_id)

    def _display_target(self, device):
        if device is None:
            self.target_status.setText("Alvo selecionado: Computador local (monitoramento ativo)")
        else:
            self.target_status.setText(
                f"Alvo selecionado: {device.name} — apenas cadastro; monitoramento permanece local"
            )

    def select_target(self):
        device = self._selected()
        if device is None:
            return
        self.selected_target_id = device.device_id
        self._display_target(device)
        self.target_changed.emit(device)
        self._update_buttons()

    def select_local(self):
        self.selected_target_id = None
        self._display_target(None)
        self.target_changed.emit(None)
        self._update_buttons()
