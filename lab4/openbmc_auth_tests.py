from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

print("=== Тест Login: Авторизация в Web UI OpenBmc ===")

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
    time.sleep(3)
    print(f"Страница открыта: {driver.current_url}")
    print(f"Заголовок страницы: '{driver.title}'")
    
    # Шаг 2: Ищем форму логина
    print("2. Поиск формы логина...")
    
    # Ищем все input поля на странице
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Найдено input полей: {len(inputs)}")
    
    # Анализируем каждое поле
    for i, inp in enumerate(inputs):
        field_type = inp.get_attribute("type")
        field_id = inp.get_attribute("id")
        field_name = inp.get_attribute("name")
        field_placeholder = inp.get_attribute("placeholder")
        
        print(f"Поле {i+1}: type='{field_type}', id='{field_id}', name='{field_name}', placeholder='{field_placeholder}'")
    
    # Шаг 3: Заполняем форму
    print("3. Заполняем форму логина...")
    
    # Находим поле для логина (type="text")
    username_field = None
    password_field = None
    
    for inp in inputs:
        field_type = inp.get_attribute("type")
        if field_type == "text":
            username_field = inp
        elif field_type == "password":
            password_field = inp
    
    if username_field and password_field:
        print("Найдены оба поля: логин и пароль")
        
        # Вводим данные
        username_field.send_keys("root")
        password_field.send_keys("0penBmc")
        print("Данные введены: root / 0penBmc")
    else:
        print("Не удалось найти поля для ввода")
    
    # Шаг 4: Находим и нажимаем кнопку Log in
    print("4. Ищем кнопку Log in...")
    
    # Ищем кнопку по тексту "Log in" (с маленькой i)
    login_button = None
    buttons = driver.find_elements(By.TAG_NAME, "button")
    
    for btn in buttons:
        if "Log in" in btn.text:
            login_button = btn
            break
    
    if login_button:
        print(f"Кнопка Log in найдена: '{login_button.text}'")
        login_button.click()
        print("Кнопка Log in нажата")
    else:
        print("Кнопка Log in не найдена")
        # Показываем какие кнопки есть
        for i, btn in enumerate(buttons):
            print(f"Кнопка {i}: '{btn.text}'")
    
    # Шаг 5: Проверяем результат
    print("5. Проверяем результат авторизации...")
    time.sleep(5)  # Увеличиваем время ожидания
    
    current_url = driver.current_url
    print(f"Текущий URL: {current_url}")
    
    # Проверяем успешность по изменению URL или наличию элементов главной страницы
    if current_url != "https://localhost:2443/#/login":
        print("Авторизация удалась! URL изменился")
        print("Тест пройден: Пользователь успешно вошел в систему")
        result = True
    else:
        # Дополнительная проверка: ищем элементы главной страницы
        try:
            # Ищем элементы которые должны быть после логина
            main_page_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'System') or contains(text(), 'Dashboard') or contains(text(), 'Overview')]")
            if main_page_elements:
                print("Авторизация удалась! Найдены элементы главной страницы")
                print("Тест пройден: Пользователь успешно вошел в систему")
                result = True
            else:
                print("Авторизация не удалась! Остались на странице логина")
                print("Тест не пройден: Не удалось войти в систему")
                result = False
        except:
            print("Авторизация не удалась!")
            print("Тест не пройден: Не удалось войти в систему")
            result = False
    
    # Делаем скриншот результата
    screenshot_name = "test1_success.png" if result else "test1_failed.png"
    driver.save_screenshot(screenshot_name)
    print(f"Скриншот сохранен: {screenshot_name}")

except Exception as e:
    print(f"Тест не пройден!: {e}")
    result = False

finally:
    # Закрываем браузер
    driver.quit()
    print(f"=== Тест Login: {'Успешно' if result else 'Ошибка'} ===")
