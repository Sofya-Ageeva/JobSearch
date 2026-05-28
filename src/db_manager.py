from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2 import sql

from config.config import Config


class DBManager:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(self) -> None:
        """Инициализация подключения к БД"""
        self.conn = psycopg2.connect(**Config.DB_CONFIG)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def create_database(self) -> None:
        """Создание базы данных если она не существует"""
        db_name = Config.DB_CONFIG['database']
        self.cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not self.cur.fetchone():
            self.cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))


    def create_tables(self) -> None:
        """Создание таблиц employers и vacancies"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id SERIAL PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                url VARCHAR(255)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(employer_id),
                vacancy_name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                url VARCHAR(255),
                requirement TEXT
            )
        """)

    def insert_employer(self, company_name: str, description: str = "", url: str = "") -> int:
        """Вставка работодателя и возврат его ID"""
        self.cur.execute("""
        INSERT INTO employers (company_name, description, url)
        VALUES (%s, %s, %s)
        ON CONFLICT (company_name) DO UPDATE
        SET description = EXCLUDED.description, url = EXCLUDED.url
        RETURNING employer_id
        """, (company_name, description, url))
        result = self.cur.fetchone()
        return int(result[0]) if result else 0

    def insert_vacancy(self, employer_id: int, vacancy_name: str, salary_from: Optional[int],
                       salary_to: Optional[int], currency: str, url: str, requirement: str) -> None:
        """Вставка вакансии"""
        self.cur.execute("""
            INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, currency, url, requirement)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (employer_id, vacancy_name, salary_from, salary_to, currency, url, requirement))

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получение списка компаний и количества вакансий у каждой"""
        self.cur.execute("""
            SELECT e.company_name, COUNT(v.vacancy_id) as vacancy_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.company_name
            ORDER BY vacancy_count DESC
        """)
        return [{'company_name': row[0], 'vacancy_count': row[1]} for row in self.cur.fetchall()]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получение списка всех вакансий с информацией о компании"""
        self.cur.execute("""
            SELECT e.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
        """)
        return [{
            'company_name': row[0],
            'vacancy_name': row[1],
            'salary_from': row[2],
            'salary_to': row[3],
            'currency': row[4],
            'url': row[5]
        } for row in self.cur.fetchall()]

    def get_avg_salary(self) -> float:
        """Получение средней зарплаты по всем вакансиям"""
        self.cur.execute("""
            SELECT AVG((salary_from + salary_to) / 2) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
        """)
        result = self.cur.fetchone()
        if result and result[0] is not None:
            return float(result[0])
        return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получение вакансий с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        self.cur.execute("""
            SELECT e.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (v.salary_from + v.salary_to) / 2 > %s
        """, (avg_salary,))
        return [{
            'company_name': row[0],
            'vacancy_name': row[1],
            'salary_from': row[2],
            'salary_to': row[3],
            'currency': row[4],
            'url': row[5]
        } for row in self.cur.fetchall()]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получение вакансий по ключевому слову"""
        self.cur.execute("""
            SELECT e.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.vacancy_name ILIKE %s
        """, (f'%{keyword}%',))
        return [{
            'company_name': row[0],
            'vacancy_name': row[1],
            'salary_from': row[2],
            'salary_to': row[3],
            'currency': row[4],
            'url': row[5]
        } for row in self.cur.fetchall()]

    def close(self) -> None:
        """Закрытие соединения с БД"""
        self.cur.close()
        self.conn.close()
