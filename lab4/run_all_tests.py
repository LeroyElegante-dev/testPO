import subprocess
import sys
import os

# Список тестов для запуска по порядку
test_files = [
    "openbmc_auth_tests.py",    # Тест 1: Успешная авторизация
    "invalid_auth_test.py",     # Тест 2: Неверные данные
    "block_account_test.py",    # Тест 3: Блокировка учетной записи
    "fans_temp_test.py",        # Тест 4: Мониторинг вентиляторов
    "inventorika_test.py"       # Тест 5: Инвентаризация
]

print("=== ЗАПУСК ВСЕХ ТЕСТОВ OPENBMC ===")
print(f"Всего тестов: {len(test_files)}")
print()

total_passed = 0
total_failed = 0

for i, test_file in enumerate(test_files, 1):
    print(f"ТЕСТ {i}/{len(test_files)}: {test_file}")
    print("-" * 40)
    
    if not os.path.exists(test_file):
        print(f"Файл не найден: {test_file}")
        total_failed += 1
        continue
    
    try:
        # Запускаем тест
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)
        
        # Выводим результат
        print(result.stdout)
        if result.stderr:
            print("Ошибки:")
            print(result.stderr)
        
        # Проверяем результат по тексту в выводе
        output = result.stdout + result.stderr
        if "Успешно" in output or "ТЕСТ ПРОЙДЕН" in output or "Тест пройден" in output:
            print(f"РЕЗУЛЬТАТ: Успешно")
            total_passed += 1
        else:
            print(f"РЕЗУЛЬТАТ: Провален")
            total_failed += 1
            
    except subprocess.TimeoutExpired:
        print("ТЕСТ ПРЕРВАН: Превышено время ожидания (5 минут)")
        total_failed += 1
    except Exception as e:
        print(f"ОШИБКА ЗАПУСКА: {e}")
        total_failed += 1
    
    print()

# Итоговый отчет
print("=" * 50)
print("ИТОГОВЫЙ ОТЧЕТ:")
print(f"Успешно: {total_passed}")
print(f"Провалено: {total_failed}")
print(f"Всего: {len(test_files)}")

if total_failed == 0:
    print("СТАТУС: Все тесты пройдены успешно")
else:
    print(f"СТАТУС: {total_failed} тестов не пройдены")
