from app.services.system_info import get_system_info


def test_get_system_info_returns_dictionary():
    info = get_system_info()

    assert isinstance(info, dict)


def test_system_info_contains_hostname():
    info = get_system_info()

    assert "hostname" in info


def test_system_info_contains_cpu():
    info = get_system_info()

    assert "cpu_count" in info
    assert "cpu_usage_percent" in info


def test_system_info_contains_memory():
    info = get_system_info()

    assert "memory_total_gb" in info
    assert "memory_usage_percent" in info


def test_system_info_contains_disk():
    info = get_system_info()

    assert "disk_total_gb" in info
    assert "disk_usage_percent" in info