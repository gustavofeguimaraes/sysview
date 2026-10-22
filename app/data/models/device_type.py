from enum import Enum


class DeviceType(str, Enum):
    """
    Tipos de dispositivos suportados pelo SysView.
    """

    COMPUTER = "computer"
    MOBILE = "mobile"
    SERVER = "server"
    NETWORK_DEVICE = "network_device"
    IOT = "iot"