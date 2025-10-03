from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=== Тест 2: Авторизация с неверными данными ===")

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

    # Шаг 2: Заполняем форму неверными данными
    print("2. Заполняем форму неверными данными...")
    
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
        # Вводим неверные данные
        username_field.send_keys("wronguser")
        password_field.send_keys("wrongpassword")
        print("Введены неверные данные: wronguser / wrongpassword")
    else:
        print("Не удалось найти поля для ввода")
        result = False
        driver.quit()
        exit()

    # Шаг 3: Нажимаем кнопку Log in
    print("3. Нажимаем кнопку Log in...")
    
    login_button = None
    buttons = driver.find_elements(By.TAG_NAME, "button")
    
    for btn in buttons:
        if "Log in" in btn.text:
            login_button = btn
            break
    
    if login_button:
        login_button.click()
        print("Кнопка Log in нажата")
    else:
        print("Кнопка Log in не найдена")

    # Шаг 4: Проверяем результат
    print("4. Проверяем результат...")
    time.sleep(3)
    
    current_url = driver.current_url
    print(f"Текущий URL: {current_url}")

    # Шаг 5: Ищем конкретное сообщение об ошибке "Invalid username or password"
    print("5. Ищем сообщение об ошибке...")
    
    # Ищем именно текст "Invalid username or password"
    error_found = False
    try:
        error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid username or password')]")
        for error_element in error_elements:
            error_text = error_element.text.strip()
            if error_text:
                print(f"Найдено сообщение об ошибке: '{error_text}'")
                error_found = True
                break
    except:
        pass

    # Дополнительная проверка: URL содержит параметр ошибки
    url_contains_error = "?next=/login" in current_url

    # Проверяем условия успешности теста
    if error_found:
        print("Тест пройден: Система показала сообщение 'Invalid username or password'")
        result = True
    elif url_contains_error:
        print("Тест пройден: URL содержит параметр ошибки (?next=/login)")
        result = True
    elif current_url == "https://localhost:2443/#/login":
        print("Тест пройден: Остались на странице логина")
        result = True
    else:
        print("Тест не пройден: Не удалось обнаружить признаков ошибки")
        result = False

    # Делаем скриншот результата
    screenshot_name = "test2_success.png" if result else "test2_failed.png"
    driver.save_screenshot(screenshot_name)
    print(f"Скриншот сохранен: {screenshot_name}")

except Exception as e:
    print(f"Тест не пройден!: {e}")
    result = False

finally:
    # Закрываем браузер
    driver.quit()
    print(f"=== Тест 2: {'Успешно' if result else 'Ошибка'} ===")
