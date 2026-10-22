import pytest

from app.data.interfaces.data_source import DataSource


class CompleteDataSource(DataSource):
    def get_dashboard(self):
        return {}

    def get_network(self):
        return {}

    def get_network_connections(self):
        return []

    def get_processes(self):
        return []

    def get_services(self):
        return []

    def get_system(self):
        return {}

    def get_source_type(self):
        return "test"

    def get_source_name(self):
        return "Fonte de teste"


def test_data_source_can_be_implemented():
    source = CompleteDataSource()

    assert source.get_source_type() == "test"
    assert source.get_source_name() == "Fonte de teste"


def test_data_source_source_info():
    source = CompleteDataSource()

    info = source.get_source_info()

    assert info == {
        "type": "test",
        "name": "Fonte de teste",
    }


def test_data_source_requires_dashboard():
    class InvalidDataSource(DataSource):
        def get_network(self):
            return {}

        def get_network_connections(self):
            return []

        def get_processes(self):
            return []

        def get_services(self):
            return []

        def get_system(self):
            return {}

        def get_source_type(self):
            return "invalid"

        def get_source_name(self):
            return "Inválida"

    with pytest.raises(TypeError):
        InvalidDataSource()


def test_data_source_requires_network():
    class InvalidDataSource(DataSource):
        def get_dashboard(self):
            return {}

        def get_network_connections(self):
            return []

        def get_processes(self):
            return []

        def get_services(self):
            return []

        def get_system(self):
            return {}

        def get_source_type(self):
            return "invalid"

        def get_source_name(self):
            return "Inválida"

    with pytest.raises(TypeError):
        InvalidDataSource()


def test_data_source_requires_processes():
    class InvalidDataSource(DataSource):
        def get_dashboard(self):
            return {}

        def get_network(self):
            return {}

        def get_network_connections(self):
            return []

        def get_services(self):
            return []

        def get_system(self):
            return {}

        def get_source_type(self):
            return "invalid"

        def get_source_name(self):
            return "Inválida"

    with pytest.raises(TypeError):
        InvalidDataSource()