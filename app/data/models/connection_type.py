from enum import Enum


class ConnectionType(str, Enum):
    """
    Define como o SysView se comunica com o dispositivo.
    """

    LOCAL = "local"
    REMOTE = "remote"
    