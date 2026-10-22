from app.data.models.device_type import DeviceType


def test_computer_device_type():
    assert DeviceType.COMPUTER.value == "computer"


def test_mobile_device_type():
    assert DeviceType.MOBILE.value == "mobile"


def test_server_device_type():
    assert DeviceType.SERVER.value == "server"


def test_network_device_type():
    assert DeviceType.NETWORK_DEVICE.value == "network_device"


def test_iot_device_type():
    assert DeviceType.IOT.value == "iot"


def test_device_type_is_string_compatible():
    assert DeviceType.COMPUTER == "computer"
    assert DeviceType.MOBILE == "mobile"