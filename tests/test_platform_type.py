from app.data.models.platform_type import PlatformType


def test_windows_platform():
    assert PlatformType.WINDOWS.value == "windows"


def test_android_platform():
    assert PlatformType.ANDROID.value == "android"


def test_platform_type_is_string_compatible():
    assert PlatformType.WINDOWS == "windows"
    assert PlatformType.ANDROID == "android"