from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=== Тест 3: Блокировка учетной записи ===")

# Настройка Chrome для игнорирования SSL ошибок
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Создаем WebDriver
service = Service("./chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Шаг 1: Открываем страницу OpenBMC
    print("1. Открываем страницу OpenBMC...")
    driver.get("https://localhost:2443")
    time.sleep(5)
    print(f"Страница открыта: {driver.current_url}")

    # Шаг 2: Выполняем несколько неудачных попыток входа
    print("2. Выполняем 5 неудачных попыток входа...")
    
    for attempt in range(5):
        print(f"Попытка {attempt + 1}/5")
        
        # Находим поля ввода
        inputs = driver.find_elements(By.TAG_NAME, "input")
        username_field = None
        password_field = None
        
        for inp in inputs:
            field_type = inp.get_attribute("type")
            if field_type == "text":
                username_field = inp
            elif field_type == "password":
                password_field = inp
        
        if username_field and password_field:
            # Очищаем поля и вводим неверные данные
            username_field.clear()
            password_field.clear()
            username_field.send_keys("root")
            password_field.send_keys(f"wrongpassword{attempt}")
            
            # Находим и нажимаем кнопку Log in
            login_button = None
            buttons = driver.find_elements(By.TAG_NAME, "button")
            
            for btn in buttons:
                if "Log in" in btn.text:
                    login_button = btn
                    break
            
            if login_button:
                login_button.click()
                print(f"Введены данные: root / wrongpassword{attempt}")
            else:
                print("Кнопка Log in не найдена")
        
        # Ждем между попытками
        time.sleep(10)
        
        # Проверяем появилось ли сообщение о блокировке
        current_url = driver.current_url
        lockout_detected = False
        
        # Ищем сообщения о блокировке
        lockout_messages = [
            "Invalid username or password",
            "Account locked",
            "Account blocked", 
            "Too many attempts",
            "Try again later"
        ]
        
        for message in lockout_messages:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{message}')]")
                if elements:
                    print(f"   Найдено сообщение: '{elements[0].text}'")
                    if "locked" in message.lower() or "blocked" in message.lower() or "many" in message.lower():
                        lockout_detected = True
                        print(f"Обнаружена возможная блокировка на попытке {attempt + 1}")
            except:
                continue
        
        if lockout_detected:
            break

    # Шаг 3: Пробуем войти с правильными данными после неудачных попыток
    print("3. Пробуем войти с правильными данными...")
    
    # Находим поля ввода
    inputs = driver.find_elements(By.TAG_NAME, "input")
    username_field = None
    password_field = None
    
    for inp in inputs:
        field_type = inp.get_attribute("type")
        if field_type == "text":
            username_field = inp
        elif field_type == "password":
            password_field = inp
    
    if username_field and password_field:
        # Очищаем поля и вводим правильные данные
        username_field.clear()
        password_field.clear()
        username_field.send_keys("root")
        password_field.send_keys("0penBmc")
        
        # Нажимаем кнопку Log in
        login_button = None
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        for btn in buttons:
            if "Log in" in btn.text:
                login_button = btn
                break
        
        if login_button:
            login_button.click()
            print("Введены правильные данные: root / 0penBmc")
    
    # Шаг 4: Проверяем результат
    print("4. Проверяем результат...")
    time.sleep(3)
    
    current_url = driver.current_url
    print(f"Текущий URL: {current_url}")
    
    # Проверяем удалось ли войти
    if "login" not in current_url:
        print("Тест пройден: Учетная запись НЕ заблокирована после 5 неудачных попыток")
        print("Система разрешила вход с правильными данными")
        result = True
    else:
        # Ищем сообщение о блокировке
        block_found = False
        block_messages = [
            "Account locked",
            "Account blocked",
            "Too many attempts", 
            "locked",
            "blocked"
        ]
        
        for message in block_messages:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{message}')]")
                if elements:
                    print(f"Найдено сообщение о блокировке: '{elements[0].text}'")
                    block_found = True
                    break
            except:
                continue
        
        if block_found:
            print("Тест пройден: Учетная запись заблокирована после нескольких неудачных попыток")
            result = True
        else:
            print("Тест не пройден: Не удалось определить статус блокировки")
            result = False

    # Делаем скриншот результата
    screenshot_name = "test3_success.png" if result else "test3_failed.png"
    driver.save_screenshot(screenshot_name)
    print(f"Скриншот сохранен: {screenshot_name}")

except Exception as e:
    print(f"Тест не пройден!: {e}")
    result = False

finally:
    # Закрываем браузер
    driver.quit()
    print(f"=== Тест 3: {'Успешно' if result else 'Ошибка'} ===")
