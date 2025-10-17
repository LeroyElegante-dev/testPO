from locust import HttpUser, task, between
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#Тестирование OpenBMC API
class OpenBMCTest(HttpUser):
    wait_time = between(1, 3)
    host = "https://localhost:2443"

    @task
    def get_system_info(self):
        """Получение информации о системе"""
        response = self.client.get("/redfish/v1/Systems/system", auth=("root", "0penBmc"), verify=False)
        print("System info:", response.status_code)

    @task
    def get_power_state(self):
        """Получение состояния питания"""
        response = self.client.get("/redfish/v1/Systems/system", auth=("root", "0penBmc"), verify=False)
        if response.status_code == 200:
            data = response.json()
            print("Power state:", data.get("PowerState", "unknown"))


#Тестирование публичного API wttr.in
class WeatherTest(HttpUser):
    wait_time = between(1, 3)
    host = "https://wttr.in"

    @task
    def get_weather(self):
        """Получение погоды для Новосибирска"""
        response = self.client.get("/Novosibirsk?format=j1")
        print("Weather:", response.status_code)
