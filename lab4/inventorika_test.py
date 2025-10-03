from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import urllib3
import re

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=== Тест 5: Проверка инвентаризации всех компонентов ===")

# Настройка Chrome для игнорирования SSL ошибок
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Создаем WebDriver
service = Service("./chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_component_detailed_data(driver, component_name, test_id):
    """Получает детальные данные для конкретного компонента"""
    detailed_info = ""
    
    try:
        # Ищем кнопку по data-test-id
        expand_buttons = driver.find_elements(By.XPATH, f"//button[@data-test-id='{test_id}']")
        
        for button in expand_buttons:
            if button.is_displayed() and button.is_enabled():
                print("    Найдена кнопка разворачивания, кликаем...")
                try:
                    # Кликаем на кнопку разворачивания
                    button.click()
                    time.sleep(3)
                    
                    # Ищем РОДИТЕЛЬСКИЙ контейнер кнопки и данные внутри него
                    parent_container = button.find_element(By.XPATH, "./ancestor::tr[1]")
                    
                    # Ищем следующую строку таблицы (развернутые данные)
                    next_row = parent_container.find_element(By.XPATH, "./following-sibling::tr[1]")
                    
                    if next_row.is_displayed():
                        next_row_text = next_row.text.strip()
                        if next_row_text and len(next_row_text) > 10:
                            detailed_info = next_row_text
                            print(f"    Найдены детальные данные для {component_name}")
                            return detailed_info
                    
                    # Если не нашли следующую строку, ищем в родительском контейнере
                    container_data = parent_container.find_elements(By.XPATH, ".//*[contains(@class, 'details')] | .//*[contains(@class, 'expanded')]")
                    for data_elem in container_data:
                        if data_elem.is_displayed():
                            data_text = data_elem.text.strip()
                            if data_text and len(data_text) > 10:
                                detailed_info = data_text
                                print(f"    Найдены детальные данные для {component_name}")
                                return detailed_info
                    
                except Exception as e:
                    print(f"    Ошибка при получении данных для {component_name}: {e}")
    
    except Exception as e:
        print(f"    Ошибка при поиске кнопки для {component_name}: {e}")
    
    return detailed_info

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

    # Шаг 2: Ищем раздел Hardware status
    print("2. Ищем раздел Hardware status...")
    
    hardware_found = False
    try:
        hardware_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Hardware status') or contains(text(), 'Hardware Status')]")
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

    # Шаг 4: Ищем компоненты на странице Inventory and LEDs
    print("4. Ищем компоненты на странице Inventory and LEDs...")
    
    target_components = [
        "System",
        "BMC manager", 
        "Chassis",
        "DIMM slot",
        "Fans",
        "Power supplies",
        "Processors",
        "Assemblies"
    ]
    
    components_data = []
    
    # Сохраняем текущую позицию страницы
    original_position = driver.execute_script("return window.pageYOffset;")
    
    for component_name in target_components:
        print(f"Ищем компонент: {component_name}")
        
        try:
            # Ищем элемент компонента на странице (якорная ссылка)
            component_elements = driver.find_elements(By.XPATH, f"//a[contains(text(), '{component_name}')] | //button[contains(text(), '{component_name}')] | //*[@role='link' and contains(text(), '{component_name}')]")
            component_element = None
            
            for elem in component_elements:
                if elem.is_displayed() and elem.is_enabled():
                    component_element = elem
                    break
            
            if component_element:
                print(f"Найден компонент: {component_name}")
                
                # Кликаем на компонент (это прокрутит страницу к нужному разделу)
                component_element.click()
                time.sleep(2)
                
                component_info = {
                    'name': component_name,
                    'count': 'N/A',
                    'table_data': '',
                    'detailed_data': ''
                }
                
                # Для компонентов без количества items (System, BMC manager, Chassis)
                if component_name in ["System", "BMC manager", "Chassis"]:
                    print(f"  Обрабатываем компонент без количества: {component_name}")
                    
                    # Парсим основную таблицу
                    main_table_data = ""
                    try:
                        # Ищем таблицу рядом с компонентом
                        tables = driver.find_elements(By.XPATH, "//table")
                        for table in tables:
                            if table.is_displayed():
                                table_text = table.text.strip()
                                if table_text and len(table_text) > 10:
                                    main_table_data = table_text
                                    break
                    except:
                        pass
                    
                    component_info['table_data'] = main_table_data
                    
                    # Получаем детальные данные для конкретного компонента
                    test_ids = {
                        "System": "hardwareStatus-button-expandSystem",
                        "BMC manager": "hardwareStatus-button-expandBmc", 
                        "Chassis": "hardwareStatus-button-expandChassis"
                    }
                    
                    test_id = test_ids.get(component_name)
                    if test_id:
                        detailed_data = get_component_detailed_data(driver, component_name, test_id)
                        component_info['detailed_data'] = detailed_data
                    
                    components_data.append(component_info)
                
                # Для компонентов с количеством items
                else:
                    print(f"  Обрабатываем компонент с количеством: {component_name}")
                    
                    # Ищем количество
                    count_found = False
                    count_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'items')]")
                    for count_element in count_elements:
                        if count_element.is_displayed():
                            count_text = count_element.text.strip()
                            if "item" in count_text.lower():
                                numbers = re.findall(r'\d+', count_text)
                                if numbers:
                                    component_count = numbers[0]
                                    component_info['count'] = component_count
                                    count_found = True
                                    print(f"    Количество: {component_info['count']} items")
                                    
                                    # Парсим таблицу только если количество > 0
                                    if component_count != '0':
                                        print(f"    Компоненты есть, парсим таблицу...")
                                        table_data = ""
                                        try:
                                            tables = driver.find_elements(By.XPATH, "//table")
                                            for table in tables:
                                                if table.is_displayed():
                                                    table_text = table.text.strip()
                                                    if table_text and len(table_text) > 10:
                                                        table_data = table_text
                                                        break
                                        except:
                                            pass
                                        
                                        component_info['table_data'] = table_data
                                    
                                    # Всегда добавляем компонент в результат
                                    components_data.append(component_info)
                                    break
                    
                    # Если не нашли количество, но компонент есть - добавляем
                    if not count_found:
                        print(f"    Количество не найдено, но компонент есть, добавляем...")
                        components_data.append(component_info)
                
                # Прокручиваем обратно к началу для следующего компонента
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
            else:
                print(f"Компонент не найден: {component_name}")
                
        except Exception as e:
            print(f"Ошибка при обработке компонента {component_name}: {e}")
            # Прокручиваем обратно к началу
            try:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            except:
                pass

    # Шаг 5: Выводим итоговую информацию
    print("5. ИТОГОВАЯ ИНФОРМАЦИЯ ОБ ИНВЕНТАРИЗАЦИИ:")
    print("=" * 60)
    
    if not components_data:
        print("Компоненты не найдены")
    else:
        for component in components_data:
            print(f"КОМПОНЕНТ: {component['name']}")
            
            if component['count'] != 'N/A':
                print(f"  Количество: {component['count']} items")
            
            if component['table_data']:
                print(f"  Данные таблицы:")
                lines = component['table_data'].split('\n')
                for i, line in enumerate(lines[:6]):
                    if line.strip():
                        print(f"    {line}")
            elif component['count'] == '0':
                print(f"  Данные таблицы: компоненты отсутствуют")
            elif component['count'] == 'N/A':
                print(f"  Данные таблицы: доступны (компоненты без количества)")
            
            if component['detailed_data']:
                print(f"  Детальные данные:")
                detailed_lines = component['detailed_data'].split('\n')
                for line in detailed_lines:
                    if line.strip():
                        print(f"    {line}")
            elif component['name'] in ["System", "BMC manager", "Chassis"]:
                print(f"  Детальные данные: не найдены")
            
            print("-" * 40)

    # Шаг 6: Проверяем результат теста
    print("6. Проверяем результат...")
    
    components_found = len(components_data)
    
    if components_found >= 3:
        print(f"Тест пройден: Найдено {components_found} компонентов инвентаризации")
        result = True
    else:
        print(f"Тест не пройден: Найдено только {components_found} компонентов")
        result = False

    # Делаем скриншот результата
    screenshot_name = "test5_success.png" if result else "test5_failed.png"
    driver.save_screenshot(screenshot_name)
    print(f"Скриншот сохранен: {screenshot_name}")

except Exception as e:
    print(f"Тест не пройден!: {e}")
    result = False

finally:
    # Закрываем браузер
    driver.quit()
    print(f"=== Тест 5: {'Успешно' if result else 'Ошибка'} ===")
