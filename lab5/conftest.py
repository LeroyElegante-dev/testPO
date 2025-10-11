import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "slow: маркировка медленных тестов"
    )

@pytest.fixture(autouse=True)
def setup_teardown():
    """Настройка перед каждым тестом и очистка после"""
    print("\n" + "="*50)
    print("Начало теста")
    yield
    print("Конец теста")
    print("="*50)
