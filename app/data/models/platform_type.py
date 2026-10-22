from enum import Enum


class PlatformType(str, Enum):
    """
    Plataformas suportadas pelo SysView.
    """

    WINDOWS = "windows"
    ANDROID = "android"