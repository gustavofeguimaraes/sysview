
import json
import logging
from datetime import datetime

from app.data.database.connection import DatabaseConnection
from app.data.models.device import Device
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType
from app.data.models.connection_type import ConnectionType


logger = logging.getLogger(__name__)


class DeviceRepository:
    """
    Persistência dos dispositivos no MySQL.

    Responsabilidades:
    - cadastrar dispositivos;
    - consultar dispositivos;
    - atualizar informações;
    - excluir dispositivos;
    - listar dispositivos cadastrados.

    Não gerencia monitores nem comunicação remota.
    """

    @staticmethod
    def _validate_device(device: Device) -> None:
        if not isinstance(device, Device):
            raise TypeError(
                "O objeto informado deve ser um Device."
            )

        if not isinstance(device.device_id, str) or not device.device_id.strip():
            raise ValueError(
                "O identificador do dispositivo é obrigatório."
            )

        if not isinstance(device.name, str) or not device.name.strip():
            raise ValueError(
                "O nome do dispositivo é obrigatório."
            )

        if not isinstance(device.device_type, DeviceType):
            raise ValueError(
                "Tipo de dispositivo inválido."
            )

        if not isinstance(device.platform, PlatformType):
            raise ValueError(
                "Plataforma inválida."
            )

        if not isinstance(device.connection_type, ConnectionType):
            raise ValueError(
                "Tipo de conexão inválido."
            )

        if device.address is not None and not isinstance(device.address, str):
            raise ValueError(
                "Endereço do dispositivo inválido."
            )

        if device.port is not None:
            if (
                isinstance(device.port, bool)
                or not isinstance(device.port, int)
                or not 1 <= device.port <= 65535
            ):
                raise ValueError(
                    "A porta deve estar entre 1 e 65535."
                )

        if not isinstance(device.online, bool):
            raise ValueError(
                "O estado online deve ser booleano."
            )

        if not isinstance(device.metadata, dict):
            raise ValueError(
                "Os metadados devem ser um dicionário."
            )

        if device.last_seen is not None and not isinstance(
            device.last_seen,
            datetime,
        ):
            raise ValueError(
                "A data do último contato é inválida."
            )

        if len(device.device_id) > 100:
            raise ValueError(
                "O identificador ultrapassa 100 caracteres."
            )

        if len(device.name) > 150:
            raise ValueError(
                "O nome ultrapassa 150 caracteres."
            )

        if device.address is not None and len(device.address) > 255:
            raise ValueError(
                "O endereço ultrapassa 255 caracteres."
            )

    @staticmethod
    def _device_values(device: Device) -> tuple:
        DeviceRepository._validate_device(device)

        metadata_json = json.dumps(
            device.metadata,
            ensure_ascii=False,
        )

        return (
            device.device_id,
            device.name,
            device.device_type.value,
            device.platform.value,
            device.connection_type.value,
            device.address,
            device.port,
            device.online,
            metadata_json,
            device.last_seen,
        )

    @staticmethod
    def _row_to_device(row: dict) -> Device:
        metadata = row.get("metadata")

        if isinstance(metadata, (bytes, bytearray)):
            metadata = metadata.decode("utf-8")

        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        if metadata is None:
            metadata = {}

        return Device(
            device_id=row["device_id"],
            name=row["name"],
            device_type=DeviceType(row["device_type"]),
            platform=PlatformType(row["platform"]),
            connection_type=ConnectionType(
                row["connection_type"]
            ),
            address=row["address"],
            port=row["port"],
            online=bool(row["online"]),
            metadata=metadata,
            last_seen=row["last_seen"],
        )

    @staticmethod
    def create(device: Device) -> bool:
        """
        Cadastra um dispositivo.

        Se o device_id já existir, o MySQL lançará
        um erro de chave duplicada.
        """
        values = DeviceRepository._device_values(device)

        sql = """
            INSERT INTO devices (
                device_id,
                name,
                device_type,
                platform,
                connection_type,
                address,
                port,
                online,
                metadata,
                last_seen
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        connection = DatabaseConnection.connect()

        try:
            cursor = connection.cursor()

            try:
                cursor.execute(sql, values)
                connection.commit()

                logger.info(
                    "Dispositivo cadastrado: %s",
                    device.device_id,
                )

                return cursor.rowcount == 1

            finally:
                cursor.close()

        except Exception:
            connection.rollback()
            logger.exception(
                "Erro ao cadastrar dispositivo: %s",
                device.device_id,
            )
            raise

        finally:
            connection.close()

    @staticmethod
    def get_by_id(device_id: str) -> Device | None:
        """
        Busca um dispositivo pelo identificador.
        """
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError(
                "O identificador do dispositivo é obrigatório."
            )

        sql = """
            SELECT
                device_id,
                name,
                device_type,
                platform,
                connection_type,
                address,
                port,
                online,
                metadata,
                last_seen
            FROM devices
            WHERE device_id = %s
        """

        connection = DatabaseConnection.connect()

        try:
            cursor = connection.cursor(dictionary=True)

            try:
                cursor.execute(sql, (device_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                return DeviceRepository._row_to_device(row)

            finally:
                cursor.close()

        finally:
            connection.close()

    @staticmethod
    def get_all() -> list[Device]:
        """
        Lista todos os dispositivos cadastrados.
        """
        sql = """
            SELECT
                device_id,
                name,
                device_type,
                platform,
                connection_type,
                address,
                port,
                online,
                metadata,
                last_seen
            FROM devices
            ORDER BY name, device_id
        """

        connection = DatabaseConnection.connect()

        try:
            cursor = connection.cursor(dictionary=True)

            try:
                cursor.execute(sql)
                rows = cursor.fetchall()

                return [
                    DeviceRepository._row_to_device(row)
                    for row in rows
                ]

            finally:
                cursor.close()

        finally:
            connection.close()

    @staticmethod
    def update(device: Device) -> bool:
        """
        Atualiza um dispositivo existente.

        Retorna False quando nenhum registro
        corresponde ao identificador.
        """
        values = DeviceRepository._device_values(device)

        sql = """
            UPDATE devices
            SET
                name = %s,
                device_type = %s,
                platform = %s,
                connection_type = %s,
                address = %s,
                port = %s,
                online = %s,
                metadata = %s,
                last_seen = %s
            WHERE device_id = %s
        """

        update_values = values[1:] + (values[0],)

        connection = DatabaseConnection.connect()

        try:
            cursor = connection.cursor()

            try:
                cursor.execute(sql, update_values)

                # rowcount pode ser zero quando os dados
                # enviados são iguais aos já armazenados.
                affected = cursor.rowcount

                if affected == 0:
                    cursor.execute(
                        "SELECT 1 FROM devices WHERE device_id = %s",
                        (device.device_id,),
                    )
                    exists = cursor.fetchone() is not None
                else:
                    exists = True

                connection.commit()

                if exists:
                    logger.info(
                        "Dispositivo atualizado: %s",
                        device.device_id,
                    )

                return exists

            finally:
                cursor.close()

        except Exception:
            connection.rollback()
            logger.exception(
                "Erro ao atualizar dispositivo: %s",
                device.device_id,
            )
            raise

        finally:
            connection.close()

    @staticmethod
    def delete(device_id: str) -> bool:
        """
        Exclui um dispositivo pelo identificador.
        """
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError(
                "O identificador do dispositivo é obrigatório."
            )

        connection = DatabaseConnection.connect()

        try:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM devices WHERE device_id = %s",
                    (device_id,),
                )

                deleted = cursor.rowcount > 0
                connection.commit()

                if deleted:
                    logger.info(
                        "Dispositivo excluído: %s",
                        device_id,
                    )

                return deleted

            finally:
                cursor.close()

        except Exception:
            connection.rollback()
            logger.exception(
                "Erro ao excluir dispositivo: %s",
                device_id,
            )
            raise

        finally:
            connection.close()

    @staticmethod
    def count() -> int:
        """
        Retorna a quantidade de dispositivos no banco.
        """
        connection = DatabaseConnection.connect()

        try:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM devices"
                )
                result = cursor.fetchone()

                return int(result[0]) if result else 0

            finally:
                cursor.close()

        finally:
            connection.close()
