import re
from datetime import datetime, timedelta

def extract_room_type(tr):
    try:
        td_element = tr.find('td', class_="hprt-table-cell-roomtype")
        if td_element:
            span_element = td_element.find('span', class_="hprt-roomtype-icon-link")
            if span_element:
                return span_element.get_text(strip=True)
    except Exception as e:
        log_error(f"Ошибка при извлечении типа номера: {e}")
    return "Не найден"

def extract_guest_count(tr):
    try:
        hprt_block = tr.find('div', class_="hprt-block")
        if hprt_block:
            bui_sr_only_span = hprt_block.find('span', class_="bui-u-sr-only")
            if bui_sr_only_span:
                match = re.search(r'\d+', bui_sr_only_span.get_text(strip=True))
                return int(match.group()) if match else 2
    except Exception as e:
        log_error(f"Ошибка при извлечении количества гостей: {e}")
    return 2

def extract_price(tr):
    try:
        price_td = tr.find('td', class_="hprt-table-cell-price")
        price = ""
        discount_price = None
        if price_td:
            price_span = price_td.find('span', class_="bui-u-sr-only")
            if price_span:
                price_text = price_span.get_text(strip=True)
                price_match = re.search(r'\d[\d\s,]*', price_text)
                price = int(price_match.group().replace(' ', '').replace(',', '')) if price_match else None

            discount_span = price_td.find('span', class_="prco-valign-middle-helper")
            if discount_span:
                discount_text = discount_span.get_text(strip=True)
                discount_match = re.search(r'\d[\d\s,]*', discount_text)
                discount_price = int(discount_match.group().replace(' ', '').replace(',', '')) if discount_match else None

            if discount_price == price:
                discount_price = None
    except Exception as e:
        log_error(f"Ошибка при извлечении цены: {e}")
    return price, discount_price

def extract_breakfast_info_and_price(tr):
    try:
        breakfast_td = tr.find('td', class_="hprt-table-cell-conditions")
        breakfast_included = "NO"
        breakfast_price = ""
        if breakfast_td:
            bui_list_body = breakfast_td.find('div', class_="bui-list__body")
            if bui_list_body:
                bui_list_description = bui_list_body.find('div', class_="bui-list__description")
                if bui_list_description:
                    span_element = bui_list_description.find('span', class_="bui-text--color-constructive")
                    if span_element:
                        breakfast_text = span_element.get_text(strip=True).lower()
                        if any(keyword in breakfast_text for keyword in ["включен завтрак", "завтрак", "включен"]):
                            breakfast_included = "YES"
                    else:
                        span_element = bui_list_description.find('span')
                        if span_element:
                            breakfast_text = span_element.get_text(strip=True)
                            breakfast_match = re.search(r'\d+', breakfast_text)
                            breakfast_price = int(breakfast_match.group()) if breakfast_match else ""


        if not breakfast_price:
            bui_list_items = breakfast_td.find_all('li', class_="bui-list__item")
            for item in bui_list_items:
                span_element = item.find('span')
                if span_element:
                    breakfast_text = span_element.get_text(strip=True)
                    if "Завтрак GEL" in breakfast_text:
                        breakfast_match = re.search(r'GEL\s+(\d+)', breakfast_text)
                        breakfast_price = int(breakfast_match.group(1)) if breakfast_match else ""
                        break

    except Exception as e:
        log_error(f"Ошибка при извлечении информации о завтраке: {e}")
    return breakfast_included, breakfast_price

def extract_available_rooms(tr):
    try:
        select_element = tr.find('select', class_="hprt-nos-select js-hprt-nos-select")
        if select_element:
            options = select_element.find_all('option')
            if options:
                last_option = options[-1]
                match = re.search(r'\d+', last_option.get_text(strip=True))
                return int(match.group()) if match else 0
    except Exception as e:
        log_error(f"Ошибка при извлечении количества доступных номеров: {e}")
    return 0

def extract_kids_bed(tr):
    try:
        td_element = tr.find('td', class_="hprt-table-cell-roomtype")
        if td_element:
            span_element = td_element.find('span', class_="hprt-roomtype-crib-label")
            if span_element and "Детская кроватка доступна по запросу" in span_element.get_text(strip=True):
                return "YES"
    except Exception as e:
        log_error(f"Ошибка при извлечении информации о детской кроватке: {e}")
    return ""

def extract_free_kids_bed(tr):
    try:
        td_element = tr.find('td', class_="hprt-table-cell-roomtype")
        if td_element:
            span_element = td_element.find('span', class_="hprt-roomtype-crib-label")
            if span_element and "Бесплатная детская кроватка" in span_element.get_text(strip=True):
                return "YES"
    except Exception as e:
        log_error(f"Ошибка при извлечении информации о бесплатной детской кроватке: {e}")
    return ""

def extract_genius(tr):
    try:
        td_element = tr.find('td', class_="hprt-table-cell-conditions")
        if td_element:
            bui_list_items = td_element.find_all('li', class_="bui-list__item")
            for item in bui_list_items:
                bui_list_body = item.find('div', class_="bui-list__body")
                if bui_list_body:
                    bui_list_description = bui_list_body.find('div', class_="bui-list__description")
                    if bui_list_description and bui_list_description.has_attr("aria-label") and \
                            bui_list_description["aria-label"] == "При входе в аккаунт может быть доступна Genius-скидка.":
                        return "YES"
    except Exception as e:
        log_error(f"Ошибка при извлечении информации о Genius: {e}")
    return "NO"

def extract_discount(tr):
    try:
        price_td = tr.find('td', class_="hprt-table-cell-price")
        if price_td:
            discount_span = price_td.find('span', class_="bui-badge__text")
            if discount_span:
                discount_text = discount_span.get_text(strip=True)
                discount_match = re.search(r'\d+', discount_text)
                return int(discount_match.group()) if discount_match else ""
    except Exception as e:
        log_error(f"Ошибка при извлечении информации о скидке: {e}")
    return ""

def update_checkin_checkout(checkin_date):
    checkin = checkin_date
    checkout = (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    return checkin, checkout

def generate_links(booking_links, params, start_date, end_date, file_name):
    current_date = start_date
    link_count = 0
    with open(file_name, 'w', encoding='utf-8') as file:
        while current_date <= end_date:
            checkin, checkout = update_checkin_checkout(current_date.strftime('%Y-%m-%d'))
            params['checkin'] = checkin
            params['checkout'] = checkout
            for link in booking_links:
                full_link = f"{link}?checkin={checkin}&checkout={checkout}&group_adults={params['group_adults']}&req_adults={params['req_adults']}&no_rooms={params['no_rooms']}&group_children={params['group_children']}&req_children={params['req_children']}&selected_currency={params['selected_currency']}"
                file.write(f"{full_link}\n")
                link_count += 1
            current_date += timedelta(days=1)
    return link_count
