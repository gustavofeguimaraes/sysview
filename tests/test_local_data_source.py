from app.data.sources.local import LocalDataSource


def test_local_data_source_returns_source_info():
    source = LocalDataSource()

    info = source.get_source_info()

    assert isinstance(info, dict)
    assert info["type"] == "local"
    assert info["name"] == "Computador local"


def test_local_data_source_returns_dashboard():
    source = LocalDataSource()

    result = source.get_dashboard()

    assert isinstance(result, dict)
    assert "cpu" in result
    assert "memory" in result
    assert "disk" in result


def test_local_data_source_returns_network():
    source = LocalDataSource()

    result = source.get_network()

    assert isinstance(result, dict)
    assert "interfaces" in result
    assert "traffic" in result
    assert "speed" in result


def test_local_data_source_returns_network_connections():
    source = LocalDataSource()

    result = source.get_network_connections()

    assert isinstance(result, list)


def test_local_data_source_returns_processes():
    source = LocalDataSource()

    result = source.get_processes()

    assert isinstance(result, list)


def test_local_data_source_returns_services():
    source = LocalDataSource()

    result = source.get_services()

    assert isinstance(result, list)


def test_local_data_source_returns_system():
    source = LocalDataSource()

    result = source.get_system()

    assert isinstance(result, dict)


def test_local_data_source_processes_have_expected_structure():
    source = LocalDataSource()

    processes = source.get_processes()

    if not processes:
        return

    process = processes[0]

    assert "pid" in process
    assert "name" in process
    assert "cpu_percent" in process
    assert "memory_percent" in process


def test_local_data_source_network_interfaces_have_expected_structure():
    source = LocalDataSource()

    network = source.get_network()

    interfaces = network["interfaces"]

    if not interfaces:
        return

    interface = interfaces[0]

    assert "name" in interface
    assert "is_up" in interface
    assert "ipv4" in interface
    assert "mac" in interface