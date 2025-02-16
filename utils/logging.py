import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from config.db_config import db_params

def log_error(message, link=None, checkin_date=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    checkin_date = checkin_date or (re.search(r'checkin=(\d{4}-\d{2}-\d{2})', link).group(1) if link else None)
    unique_id = random.randint(1000, 9999)

    site = 'booking' if link else None
    url = link if link else None
    error_text = message if message else None
    update_date = timestamp

    try:
        connection = mysql.connector.connect(**db_params)
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO logging1 (id, site, url, checkin, error_text, update_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (unique_id, site, url, checkin_date, error_text, update_date))
            connection.commit()
    except Error as e:
        print(f"Error logging error to database: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

def log_processed_link():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    unique_id = random.randint(1000, 9999)

    try:
        connection = mysql.connector.connect(**db_params)
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO logging1 (id, update_date)
            VALUES (%s, %s)
            """
            cursor.execute(insert_query, (unique_id, timestamp))
            connection.commit()
    except Error as e:
        print(f"Error logging processed link to database: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
