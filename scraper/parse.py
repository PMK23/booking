from bs4 import BeautifulSoup
from utils.helpers import extract_room_type, extract_guest_count, extract_price, extract_breakfast_info_and_price, \
    extract_available_rooms, extract_kids_bed, extract_free_kids_bed, extract_genius, extract_discount
from utils.logging import log_error
from scraper.save import save_to_db

def parse_page(response, link, links_generated, row_count):
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        hprt_container = soup.find('table', class_="hprt-table")
        if not hprt_container:
            log_error(f"Блок <table class='hprt-table'> не найден на странице: {link}", link=link)
            return row_count

        tbody = hprt_container.find('tbody')
        if not tbody:
            log_error(f"Элемент <tbody> не найден внутри <table class='hprt-table'> на странице: {link}", link=link)
            return row_count

        tr_elements = tbody.find_all('tr')
        tr_with_data_block_id = [tr for tr in tr_elements if tr.get('data-block-id')]
        if not tr_with_data_block_id:
            log_error(f"Элементы <tr> с атрибутом data-block-id не найдены на странице: {link}", link=link)
            return row_count

        kids_bed_found = False
        free_kids_bed_found = False

        for tr in tr_with_data_block_id:
            data_block_id = tr['data-block-id'].split('_')[0]
            room_type_text = extract_room_type(tr)
            guest_count = extract_guest_count(tr)
            price, discount_price = extract_price(tr)
            breakfast_included, breakfast_price = extract_breakfast_info_and_price(tr)
            available_rooms = extract_available_rooms(tr)
            genius = extract_genius(tr)
            discount = extract_discount(tr)

            if not kids_bed_found:
                kids_bed = extract_kids_bed(tr)
                if kids_bed:
                    kids_bed_found = True

            if not free_kids_bed_found:
                free_kids_bed = extract_free_kids_bed(tr)
                if free_kids_bed:
                    free_kids_bed_found = True

            save_to_db(link, data_block_id, room_type_text, guest_count, price, discount_price, breakfast_included,
                       available_rooms, breakfast_price, kids_bed, free_kids_bed, genius, discount, links_generated, row_count)
            row_count += 1
    except Exception as e:
        log_error(f"Ошибка при парсинге HTML: {e}", link=link)
    return row_count
