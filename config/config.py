import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'hh_vacancies'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }

    EMPLOYERS = [
        'yandex',
        'google',
        'sberbank',
        'tinkoff',
        'ozon',
        'wildberries',
        'kaspersky',
        'vkontakte',
        'avito',
        'epam'
    ]

    HH_API_URL = 'https://api.hh.ru/vacancies'
