# import sys
# from src.api import HHApi
from src.data_loader import DataLoader
from src.db_manager import DBManager


def main() -> None:
    """Главная функция программы"""
    print("Поиск вакансий с сайта hh.ru")

    db_manager = None
    try:
        # Инициализация БД
        print("Подключение к базе данных...")
        db_manager = DBManager()
        db_manager.create_database()
        db_manager.create_tables()
        print("База данных готова\n")

        # Получение данных с hh.ru
        print("Загрузка данных из файла hh_vacancies.json...")
        loader = DataLoader('data/hh_vacancies.json')
        all_vacancies = loader.load_vacancies()

        if not all_vacancies:
            print("Нет данных для загрузки. Проверьте файл hh_vacancies.json")
            return

        # Словарь для хранения уже добавленных компаний
        employers_dict = {}

        # Заполнение таблиц данными из файла
        for vacancy in all_vacancies:
            # Получаем название компании
            employer_data = vacancy.get('employer', {})
            company_name = employer_data.get('name', 'Unknown Company')

            # Добавляем компанию, если ещё не добавлена
            if company_name not in employers_dict:
                employer_id = db_manager.insert_employer(company_name)
                employers_dict[company_name] = employer_id
                print(f"Добавлена компания: {company_name}")
            else:
                employer_id = employers_dict[company_name]

            # Получаем данные о зарплате
            salary = vacancy.get('salary')
            salary_from = salary.get('from') if salary else None
            salary_to = salary.get('to') if salary else None
            currency = salary.get('currency') if salary else ''

            # Добавляем вакансию
            db_manager.insert_vacancy(
                employer_id=employer_id,
                vacancy_name=vacancy.get('name', ''),
                salary_from=salary_from,
                salary_to=salary_to,
                currency=currency,
                url=vacancy.get('alternate_url', ''),
                requirement=vacancy.get('snippet', {}).get('requirement', '')
            )

        print(f"\nДанные загружены: {len(employers_dict)} компаний, {len(all_vacancies)} вакансий\n")

        # Взаимодействие с пользователем
        while True:
            print("\n" + "=" * 60)
            print("ГЛАВНОЕ МЕНЮ:")
            print("1. Список компаний и количество вакансий")
            print("2. Список всех вакансий")
            print("3. Средняя зарплата по всем вакансиям")
            print("4. Вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")
            print("0. Выход")
            print("=" * 60)

            choice = input("Выберите действие (0-5): ").strip()

            if choice == "0":
                print("\nДо свидания!")
                break

            elif choice == "1":
                companies = db_manager.get_companies_and_vacancies_count()
                print("\nКомпании и найденные вакансии:")
                for c in companies:
                    print(f"  • {c['company_name']}: {c['vacancy_count']} вакансий")

            elif choice == "2":
                vacancies = db_manager.get_all_vacancies()
                print("\nВсе вакансии:")
                if not vacancies:
                    print("  Нет вакансий в базе данных")
                for i, v in enumerate(vacancies, 1):
                    salary_info = f"{v['salary_from']}-{v['salary_to']} {v['currency']}" if v['salary_from'] or v[
                        'salary_to'] else "з/п не указана"
                    print(f"  {i}. {v['company_name']} | {v['vacancy_name']} | {salary_info}")

            elif choice == "3":
                avg_salary = db_manager.get_avg_salary()
                if avg_salary:
                    print(f"\nСредняя заработная плата: {int(avg_salary):,} руб.")
                else:
                    print("\nНет данных для расчёта средней зарплаты")

            elif choice == "4":
                vacancies = db_manager.get_vacancies_with_higher_salary()
                print("\nВакансии с зарплатой выше среднего уровня:")
                if not vacancies:
                    print("  Нет вакансий с зарплатой выше средней")
                for i, v in enumerate(vacancies, 1):
                    print(f"  {i}. {v['vacancy_name']} - {v['salary_from']}-{v['salary_to']} {v['currency']}")

            elif choice == "5":
                keyword = input("\nВведите ключевое слово для поиска: ").strip()
                if keyword:
                    vacancies = db_manager.get_vacancies_with_keyword(keyword)
                    print(f"\nВакансии по запросу '{keyword}':")
                    if not vacancies:
                        print(f"Нет вакансий, содержащих '{keyword}'")
                    for i, v in enumerate(vacancies, 1):
                        print(f"  {i}. {v['vacancy_name']} ({v['company_name']})")
                else:
                    print("Ключевое слово не может быть пустым")

            else:
                print("Неверный ввод. Пожалуйста, выберите 0-5")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if db_manager:
            db_manager.close()
            print("\nСоединение с базой данных закрыто")


if __name__ == "__main__":
    main()
