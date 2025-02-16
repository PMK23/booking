import requests
import time
import concurrent.futures
from datetime import datetime, timedelta
from config.config import API_URL
from utils.logging import log_error, log_processed_link
from scraper.fetch import fetch_page
from scraper.parse import parse_page
from utils.helpers import generate_links

def main():
    while True:
        print("Начало выполнения скрипта...")
        row_count = 0 
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            booking_links = [item["Booking.com"].replace("?", "") for item in data if
                             item.get("Booking.com") and item["Booking.com"] != "None"]

            params = {
                'group_adults': 2,
                'req_adults': 2,
                'no_rooms': 1,
                'group_children': 0,
                'req_children': 0,
                'selected_currency': 'GEL'
            }

            current_datetime = datetime.now()


            intervals = [
                (current_datetime + timedelta(days=0), current_datetime + timedelta(days=2), 'LINKS1.txt', 4),
                (current_datetime + timedelta(days=3), current_datetime + timedelta(days=6), 'LINKS2.txt', 8),
                (current_datetime + timedelta(days=7), current_datetime + timedelta(days=28), 'LINKS3.txt', 12),
                (current_datetime + timedelta(days=35), current_datetime + timedelta(days=35), 'LINKS4.txt', 19),
                (current_datetime + timedelta(days=45), current_datetime + timedelta(days=89), 'LINKS5.txt', 25)
            ]

            for start_date, end_date, file_name, interval_hours in intervals:
                link_count = generate_links(booking_links, params, start_date, end_date, file_name)
                print(f"Ссылки для интервала {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')} успешно сохранены в файл {file_name}. Всего сформировано {link_count} ссылок.")


                log_error(
                    message="Ссылки сгенерированы"
                )

                try:
                    with open(file_name, 'r', encoding='utf-8') as file:
                        links = file.readlines()
                except IOError as e:
                    log_error(f"Ошибка при чтении файла: {e}", link=link)

                print(f"Начало парсинга страниц для интервала {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    link_number = 1
                    for link in links:
                        link = link.strip()
                        futures.append(executor.submit(fetch_and_parse, link, link_number, link_count, row_count))
                        time.sleep(random.uniform(1, 6))
                        link_number += 1

                    for future in concurrent.futures.as_completed(futures):
                        try:
                            row_count = future.result()
                        except Exception as e:
                            log_error(f"Ошибка при выполнении задачи: {e}", link=link)

                print(f"Парсинг страниц для интервала {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')} завершен.")


                print(f"Скрипт завершил выполнение для интервала {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}. Ожидание {interval_hours} часов до следующего запуска...")
                time.sleep(interval_hours * 60 * 60)

        except requests.exceptions.RequestException as e:
            log_error(f"Ошибка при выполнении запроса к API: {e}", link=link)

def fetch_and_parse(link, link_number, links_generated, row_count):
    start_time = datetime.now()
    response = fetch_page(link)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status_code = response.status_code if response else None
    if response and response.status_code == 200:
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        print(f"Обработана ссылка {link_number}: {link} - обработана за {processing_time:.2f} - Получены данные: ДА")
        row_count = parse_page(response, link, links_generated, row_count)
        log_processed_link()
    else:
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        print(f"Обработана ссылка {link_number}: {link} - обработана за {processing_time:.2f} - Получены данные: НЕТ")
        log_error(
            f"Неудачный запрос для {link}: {status_code if status_code else 'No response'}",
            link=link
        )
        log_processed_link()
    return row_count

if __name__ == "__main__":
    main()
