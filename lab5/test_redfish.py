import pytest
import requests
import json
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:2443/redfish/v1"
USERNAME = "root"
PASSWORD = "0penBmc"
TIMEOUT = 30

AUTH_TOKEN = None


@pytest.fixture(scope="session")
def auth_session():
    global AUTH_TOKEN
    
    session = requests.Session()
    session.verify = False

    response = session.post(
        f"{BASE_URL}/SessionService/Sessions",
        json={"UserName": USERNAME, "Password": PASSWORD}
    )
    jdata=response.headers
    print(jdata)
    if response.status_code == 201:
        AUTH_TOKEN = response.headers['X-Auth-Token']
        session.headers['X-Auth-Token'] = AUTH_TOKEN
    print(session.headers)
    yield session

    try:
        session.delete(f"{BASE_URL}/SessionService/Sessions/{response.json().get('Id', '')}", timeout=TIMEOUT)
    except:
        pass
    session.close()

@pytest.fixture
def system_info(auth_session):
    response = auth_session.get(f"{BASE_URL}/Systems/system", timeout=TIMEOUT)
    return response.json()

class TestRedfishAPI:
    
    def test_01_authentication(self, auth_session):
        print("Тестирование аутентификации...")
        
        response = auth_session.get(f"{BASE_URL}/", timeout=TIMEOUT)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert "RedfishVersion" in data, "Ответ не содержит RedfishVersion"
        assert "Systems" in data, "Ответ не содержит Systems"
        
        print("Аутентификация успешна")
    
    def test_02_system_info(self, auth_session, system_info):
        print("Тестирование информации о системе...")
        
        required_fields = ["@odata.id", "@odata.type"]
        for field in required_fields:
            assert field in system_info, f"Ответ не содержит обязательное поле {field}"
        
        assert "Status" in system_info, "Ответ не содержит Status"
        
        if "PowerState" in system_info:
            valid_power_states = ["On", "Off", "PoweringOn", "PoweringOff"]
            power_state = system_info.get("PowerState")
            assert power_state in valid_power_states, f"Недопустимый PowerState: {power_state}"
            print(f"PowerState: {power_state}")
        else:
            print("PowerState не найден в ответе")
        
        if "Model" in system_info:
            print(f"Model: {system_info['Model']}")
        else:
            print("Model не найден в ответе")
        
        useful_fields = ["Name", "Id", "Manufacturer", "Model", "SerialNumber", "PartNumber"]
        found_fields = [field for field in useful_fields if field in system_info]
        assert len(found_fields) > 0, "Не найдено ни одного полезного поля в информации о системе"
        
        print(f"Найдены поля: {found_fields}")
        print("Информация о системе получена успешно")
    
    def test_03_power_management(self, auth_session, system_info):
        print("Тестирование управления питанием...")
        
        assert "Actions" in system_info, "Ответ не содержит Actions"
        assert "#ComputerSystem.Reset" in system_info["Actions"], "Не найдено действие ComputerSystem.Reset"
        
        current_power_state = system_info.get("PowerState", "Unknown")
        print(f"Текущее состояние питания: {current_power_state}")
        
        test_reset_types = ["GracefulRestart", "ForceRestart"]
        
        for reset_type in test_reset_types:
            print(f"Тестирование команды: {reset_type}")
            
            power_action = {
                "ResetType": reset_type
            }
            
            try:
                response = auth_session.post(
                    f"{BASE_URL}/Systems/system/Actions/ComputerSystem.Reset",
                    json=power_action,
                    timeout=TIMEOUT
                )
                
                assert response.status_code in [200, 202, 204, 400], \
                    f"Неожиданный статус для {reset_type}: {response.status_code}"
                
                if response.status_code in [200, 202, 204]:
                    print(f"Команда '{reset_type}' принята сервером")
                else:
                    print(f"Команда '{reset_type}' недоступна")
                    
            except Exception as e:
                print(f"Ошибка при отправке команды {reset_type}: {e}")
        
        print("Тестирование управления питанием завершено")
    
    def test_04_cpu_temperature(self, auth_session):
        print("Тестирование температуры CPU...")
        
        thermal_url = f"{BASE_URL}/Chassis/chassis/ThermalSubSystem"
        
        try:
            print(f"Пробуем URL: {thermal_url}")
            
            headers = {'X-Auth-Token': AUTH_TOKEN} if AUTH_TOKEN else {}
            
            response = auth_session.get(thermal_url, headers=headers, timeout=TIMEOUT, verify=False)
            print(f"qqqqqqqqqqqqq: {dict(response.headers)}")
            print(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                thermal_data = response.json()
                print(f"Thermal данные найдены по URL: {thermal_url}")
                print(f"Структура данных: {list(thermal_data.keys())}")
                
                temperatures = []
                
                if "Temperatures" in thermal_data and thermal_data["Temperatures"]:
                    temperatures = thermal_data["Temperatures"]
                
                if not temperatures:
                    pytest.skip("Температурные датчики не найдены в Thermal данных")
                
                print(f"Найдено температурных датчиков: {len(temperatures)}")
                
                for i, temp_sensor in enumerate(temperatures):
                    sensor_name = temp_sensor.get("Name", f"Unknown_{i}")
                    sensor_id = temp_sensor.get("SensorNumber", i)
                    current_temp = temp_sensor.get("ReadingCelsius")
                    status = temp_sensor.get("Status", {})
                    
                    print(f"Датчик {i+1}: {sensor_name} (ID: {sensor_id}), Температура: {current_temp}C, Статус: {status}")
                    
                    if current_temp is not None:
                        upper_critical = temp_sensor.get("UpperThresholdCritical")
                        upper_fatal = temp_sensor.get("UpperThresholdFatal")
                        
                        if upper_critical is not None:
                            assert current_temp <= upper_critical, \
                                f"Температура {sensor_name} превышает критический порог: {current_temp} > {upper_critical}"
                        
                        if upper_fatal is not None:
                            assert current_temp <= upper_fatal, \
                                f"Температура {sensor_name} превышает фатальный порог: {current_temp} > {upper_fatal}"
                        
                        assert -20 <= current_temp <= 120, \
                            f"Температура {sensor_name} вне разумных пределов: {current_temp}C"
                        
                        print(f"Температура {sensor_name} в норме")
                    else:
                        print(f"Датчик {sensor_name} не показывает температуру")
                
                print("Проверка температуры завершена успешно")
            else:
                print(f"URL {thermal_url} недоступен, статус: {response.status_code}")
                #pytest.skip("Thermal endpoint не найден")
                    
        except Exception as e:
            print(f"Ошибка при запросе {thermal_url}: {e}")
            #pytest.skip(f"Ошибка доступа к Thermal endpoint: {e}")
    
    def test_05_cpu_sensors_consistency(self, auth_session):
        print("Тестирование согласованности датчиков CPU...")
        
        response = auth_session.get(f"{BASE_URL}/Systems/system", timeout=TIMEOUT)
        assert response.status_code == 200, "Не удалось получить информацию о системе"
        
        system_data = response.json()
        
        cpu_info = {}
        
        cpu_related_fields = [
            "ProcessorSummary", "Model", "Name", "Id", "Status", 
            "PowerState", "Manufacturer", "SerialNumber"
        ]
        
        for field in cpu_related_fields:
            if field in system_data:
                cpu_info[field] = system_data[field]
                print(f"Redfish {field}: {system_data[field]}")
        
        assert len(cpu_info) > 0, "Не удалось получить информацию о CPU через Redfish"
        
        try:
            response = auth_session.get(f"{BASE_URL}/Systems/system/Processors", timeout=TIMEOUT)
            if response.status_code == 200:
                processors_data = response.json()
                if "Members" in processors_data:
                    print(f"Найдено процессоров: {len(processors_data['Members'])}")
        except:
            print("Детальная информация о процессорах недоступна")
        
        print("Базовая проверка датчиков CPU завершена")

    def test_06_session_management(self, auth_session):
        print("Тестирование управления сессиями...")
        
        response = auth_session.get(f"{BASE_URL}/SessionService", timeout=TIMEOUT)
        assert response.status_code == 200, "Не удалось получить информацию о SessionService"
        
        session_service = response.json()
        
        if "SessionTimeout" in session_service:
            print(f"Таймаут сессии: {session_service['SessionTimeout']} минут")
        else:
            print("SessionTimeout не найден")
        
        if "Sessions" in session_service:
            print("Сервис сессий доступен")
        else:
            print("Информация о сессиях недоступна")

def test_redfish_discovery():
    session = requests.Session()
    session.verify = False
    
    auth_url = f"{BASE_URL}/SessionService/Sessions"
    auth_data = {
        "UserName": USERNAME,
        "Password": PASSWORD
    }
    
    try:
        response = session.post(auth_url, json=auth_data, timeout=TIMEOUT)
        if response.status_code == 201:
            session.headers["X-Auth-Token"] = response.headers["X-Auth-Token"]
    except:
        pass
    
    response = session.get(BASE_URL, timeout=TIMEOUT)
    if response.status_code == 200:
        data = response.json()
        print("Доступные endpoints Redfish:")
        for key, value in data.items():
            if isinstance(value, dict) and "@odata.id" in value:
                print(f"  - {key}: {value['@odata.id']}")

if __name__ == "__main__":
    test_redfish_discovery()
