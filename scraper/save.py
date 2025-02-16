import mysql.connector
from mysql.connector import Error
from config.db_config import db_params
from utils.logging import log_error
import random
from datetime import datetime
import re

def save_to_db(link, data_block_id, room_type_text, guest_count, price, discount_price, breakfast_included,
               available_rooms, breakfast_price, kids_bed, free_kids_bed, genius, discount, links_generated, row_count):
    id_value = random.randint(10000, 99999)
    site = "booking"
    url = link
    checkin_date = re.search(r'checkin=(\d{4}-\d{2}-\d{2})', link).group(1)
    sub = data_block_id
    number_of_available_rooms = available_rooms
    guests = guest_count
    price_value = price
    price2_value = discount_price if discount_price else ""
    update_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        connection = mysql.connector.connect(**db_params)
        if connection.is_connected():
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO hotels (id, site, url, checkin, sub, breakfast_included, breakfast_price,
                                 number_of_available_rooms, guests, price, price2, update_date, kids_bed, free_kids_bed, genius, discount, links_generated, row_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_query, (id_value, site, url, checkin_date, sub, breakfast_included, breakfast_price,
                                          number_of_available_rooms, guests, price_value, price2_value, update_date, kids_bed, free_kids_bed, genius, discount, links_generated, row_count))

            connection.commit()
            log_error(
                f"Сохранено в базу данных: {id_value}, {site}, {url}, {checkin_date}, {sub}, {breakfast_included}, {breakfast_price}, {number_of_available_rooms}, {guests}, {price_value}, {price2_value}, {update_date}, {kids_bed}, {free_kids_bed}, {genius}, {discount}, {links_generated}, {row_count}",
                link=link
            )

    except Error as e:
        log_error(f"Ошибка при сохранении данных в базу данных: {e}", link=link)
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
