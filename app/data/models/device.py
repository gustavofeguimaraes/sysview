from dataclasses import dataclass, field
from datetime import datetime

from app.data.models.connection_type import ConnectionType
from app.data.models.device_type import DeviceType
from app.data.models.platform_type import PlatformType


@dataclass
class Device:
    """
    Representa um dispositivo gerenciado pelo SysView.

    O modelo é independente da forma de comunicação.
    """

    device_id: str
    name: str
    device_type: DeviceType
    platform: PlatformType
    connection_type: ConnectionType

    address: str | None = None
    port: int | None = None

    online: bool = False

    metadata: dict = field(default_factory=dict)

    last_seen: datetime | None = None

    def mark_online(self) -> None:
        self.online = True
        self.last_seen = datetime.now()

    def mark_offline(self) -> None:
        self.online = False

    def get_source_info(self) -> dict:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type.value,
            "platform": self.platform.value,
            "connection_type": self.connection_type.value,
            "address": self.address,
            "port": self.port,
            "online": self.online,
            "last_seen": self.last_seen,
        }