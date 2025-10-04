from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=== Тест 4: Проверка температуры компонентов через Redfish API ===")

# Настройка Chrome для игнорирования SSL ошибок
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Создаем WebDriver
service = Service("./chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Шаг 1: Логинимся в систему
    print("1. Выполняем вход в систему...")
    driver.get("https://localhost:2443")
    time.sleep(5)
    
    # Заполняем форму логина
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for inp in inputs:
        field_type = inp.get_attribute("type")
        if field_type == "text":
            inp.send_keys("root")
        elif field_type == "password":
            inp.send_keys("0penBmc")
    
    # Нажимаем кнопку Log in
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if "Log in" in btn.text:
            btn.click()
            break
    
    time.sleep(5)
    
    # Проверяем успешность логина
    if "login" in driver.current_url:
        print("Ошибка: Не удалось войти в систему")
        result = False
        driver.quit()
        exit()
    
    print("Успешный вход в систему")
    print(f"Текущий URL: {driver.current_url}")

    # Шаг 2: Переходим на страницу Redfish Thermal
    print("2. Переходим на страницу Thermal данных...")
    
    thermal_url = "https://localhost:2443/redfish/v1/Chassis/chassis/Thermal"
    driver.get(thermal_url)
    time.sleep(5)
    
    print(f"Открыта страница: {driver.current_url}")
    
    # Шаг 3: Ищем текст на странице
    print("3. Ищем информацию о температуре...")
    
    # Получаем весь текст страницы
    page_text = driver.find_element(By.TAG_NAME, "body").text
    print("Текст страницы:")
    print(page_text)
    
    # Ищем ключевые фразы
    if "thermal not found" in page_text.lower():
        print("РЕЗУЛЬТАТ: Thermal not found - температура не обнаружена")
        result = True
    elif "Critical" in page_text:
        print("РЕЗУЛЬТАТ: Critical - критическое состояние температуры")
        result = True
    elif "Temperatures" in page_text or "Temperature" in page_text:
        print("РЕЗУЛЬТАТ: Данные о температуре найдены")
        result = True
    else:
        print("РЕЗУЛЬТАТ: Информация о температуре не найдена")
        result = False

    # Делаем скриншот результата
    screenshot_name = "test4_success.png" if result else "test4_failed.png"
    driver.save_screenshot(screenshot_name)
    print(f"Скриншот сохранен: {screenshot_name}")

except Exception as e:
    print(f"Тест не пройден!: {e}")
    result = False

finally:
    # Закрываем браузер
    driver.quit()
    print(f"=== Тест 4: {'Успешно' if result else 'Ошибка'} ===")
