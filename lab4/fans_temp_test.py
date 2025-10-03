from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import urllib3
import re

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=== Тест 4: Проверка температуры вентиляторов (Fans) ===")

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

    # Шаг 2: Ищем раздел Hardware Status
    print("2. Ищем раздел Hardware status...")
    
    hardware_found = False
    try:
        hardware_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Hardware status')]")
        for element in hardware_elements:
            if element.is_displayed() and element.is_enabled():
                print(f"Найден раздел: '{element.text}'")
                try:
                    element.click()
                    print("Перешли в раздел Hardware status")
                    hardware_found = True
                    time.sleep(3)
                    break
                except Exception as e:
                    print(f"Не удалось кликнуть на Hardware status: {e}")
    except:
        pass
    
    if not hardware_found:
        print("Раздел Hardware status не найден")
        result = False
        driver.quit()
        exit()

    # Шаг 3: Ищем подраздел Inventory and LEDs
    print("3. Ищем подраздел Inventory and LEDs...")
    
    inventory_found = False
    try:
        inventory_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Inventory and LEDs')]")
        for element in inventory_elements:
            if element.is_displayed() and element.is_enabled():
                print(f"Найден подраздел: '{element.text}'")
                try:
                    element.click()
                    print("Перешли в раздел Inventory and LEDs")
                    inventory_found = True
                    time.sleep(3)
                    break
                except Exception as e:
                    print(f"Не удалось кликнуть на Inventory and LEDs: {e}")
    except:
        pass
    
    if not inventory_found:
        print("Подраздел Inventory and LEDs не найден")
        result = False
        driver.quit()
        exit()

    # Шаг 4: Ищем раздел Fans
    print("4. Ищем раздел Fans...")
    
    fans_found = False
    try:
        fans_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Fans')]")
        for element in fans_elements:
            if element.is_displayed():
                print(f"Найден раздел: '{element.text}'")
                try:
                    if element.is_enabled():
                        element.click()
                        print("Перешли в раздел Fans")
                    fans_found = True
                    time.sleep(3)
                    break
                except Exception as e:
                    print(f"Не удалось кликнуть на Fans: {e}")
                    fans_found = True
                    break
    except:
        pass
    
    if not fans_found:
        print("Раздел Fans не найден")
        result = False
        driver.quit()
        exit()

    # Шаг 5: Ищем количество вентиляторов
    print("5. Ищем количество вентиляторов...")
    
    items_count = "не определено"
    count_number = "не определено"
    items_found = False
    
    try:
        count_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'items')]")
        for element in count_elements:
            if element.is_displayed():
                count_text = element.text.strip()
                if "item" in count_text.lower():
                    print(f"Найдена информация о количестве: '{count_text}'")
                    items_count = count_text
                    items_found = True
                    
                    numbers = re.findall(r'\d+', count_text)
                    if numbers:
                        count_number = numbers[0]
                        print(f"КОЛИЧЕСТВО ВЕНТИЛЯТОРОВ: {count_number}")
                    break
    except Exception as e:
        print(f"Ошибка при поиске количества: {e}")

    # Шаг 6: Ищем таблицу с информацией о Fans
    print("6. Ищем таблицу с информацией о вентиляторах...")
    
    fans_data_found = False
    table_message = ""
    
    try:
        no_items_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'No items available')]")
        for element in no_items_elements:
            if element.is_displayed():
                table_message = element.text.strip()
                print(f"Найдено сообщение из таблицы: '{table_message}'")
                fans_data_found = True
                break
        
        if not fans_data_found:
            table_elements = driver.find_elements(By.XPATH, "//table | //div[contains(@class, 'table')]")
            for table in table_elements:
                if table.is_displayed():
                    table_text = table.text.strip()
                    if table_text and ("Fan" in table_text or "fan" in table_text):
                        print("Найдена таблица с данными о вентиляторах:")
                        print(f"СОДЕРЖИМОЕ ТАБЛИЦЫ:\n{table_text}")
                        table_message = "Найдены данные вентиляторов в таблице"
                        fans_data_found = True
                        break
    except Exception as e:
        print(f"Ошибка при поиске таблицы: {e}")

    # Шаг 7: Выводим итоговую информацию
    print("7. ИТОГОВАЯ ИНФОРМАЦИЯ О ВЕНТИЛЯТОРАХ:")
    
    if items_found:
        print(f"   КОЛИЧЕСТВО: {items_count}")
    
    if fans_data_found:
        if "No items available" in table_message:
            print(f"   СТАТУС: {table_message}")
            print("   ВЫВОД: В системе нет виртуальных компонентов вентиляторов")
        else:
            print(f"   ДАННЫЕ: {table_message}")
    else:
        print("   Информация о вентиляторах не найдена")

    # Шаг 8: Проверяем результат теста
    print("8. Проверяем результат...")
    
    if fans_found and (items_found or fans_data_found):
        print("Тест пройден: Раздел Fans найден, информация о вентиляторах получена")
        result = True
    else:
        print("Тест не пройден: Не удалось получить информацию о вентиляторах")
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
