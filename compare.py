import os
import re
import subprocess
import sys
import time


def parse_timing(output_text):
    """
    Извлекает время из вывода программы.
    """

    if not output_text:

        return {}

    timings = {}

    patterns = {
        'Загрузка данных': [r'время:\s+([\d.]+)\s+сек', r'Загрузка данных:\s+([\d.]+)\s+сек'],
        'Фильтрация': [r'Время:\s+([\d.]+)\s+сек', r'Фильтрация по гарантии:\s+([\d.]+)\s+сек'],
        'Поиск клиник': [r'Время:\s+([\d.]+)\s+сек', r'Поиск проблемных клиник:\s+([\d.]+)\s+сек'],
        'Отчет калибровки': [r'Время:\s+([\d.]+)\s+сек', r'Отчет по калибровке:\s+([\d.]+)\s+сек'],
        'Сводная таблица': [r'Время:\s+([\d.]+)\s+сек', r'Создание сводной таблицы:\s+([\d.]+)\s+сек'],
        'Сохранение': [r'Время сохранения:\s+([\d.]+)\s+сек', r'Сохранение отчетов:\s+([\d.]+)\s+сек'],
        'ОБЩЕЕ': [r'ОБЩЕЕ ВРЕМЯ ВЫПОЛНЕНИЯ:\s+([\d.]+)\s+сек',
                  r'ОБЩЕЕ ВРЕМЯ:\s+([\d.]+)\s+сек']
    }

    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, output_text, re.IGNORECASE)
            if match:
                timings[key] = float(match.group(1))
                break

    return timings


def run_script(script_name, folder):
    """
    Запускает скрипт и возвращает время выполнения.
    """

    print(f"\n  Запуск {script_name}...")

    try:
        start = time.time()
        result = subprocess.run(
            [sys.executable, script_name, folder],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        elapsed = time.time() - start
        timings = parse_timing(result.stdout)
        timings['Реальное_время'] = elapsed

        return timings

    except Exception as e:
        print(f"  Ошибка: {e}")

        return {}


def compare():
    folder = "async_data"

    # запускаем оба скрипта
    async_times = run_script("асинхронка2.py", folder)
    thread_times = run_script("многопоточность.py", folder)

    # выводим таблицу
    print("\n" + "=" * 82)
    print(f"{'Операция':<20}     {'Асинхронно':>12}      {'Многопоточно':>12} {'Разница':>12} {'Кто быстрее':>12}")
    print("=" * 82)

    # все операции для сравнения
    operations = ['Загрузка данных', 'Фильтрация', 'Поиск клиник',
                  'Отчет калибровки', 'Сводная таблица', 'Сохранение', 'ОБЩЕЕ']

    for op in operations:
        a = async_times.get(op, 0)
        t = thread_times.get(op, 0)

        if a > 0 or t > 0:
            diff = a - t
            if a < t and a > 0:
                winner = "асинхр"
            elif t < a and t > 0:
                winner = "многопот"
            elif a > 0 and t > 0 and abs(a - t) < 0.01:
                winner = "="
            else:
                winner = "нет данных"

            print(f"{op:<20} {a:>11.2f} сек {t:>11.2f} сек {diff:>+11.2f} сек {winner:>12}")

    print("=" * 82)


if __name__ == "__main__":
    compare()