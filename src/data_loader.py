import json
from typing import Any, Dict, List


class DataLoader:
    """Класс для загрузки данных из локального JSON-файла"""

    def __init__(self, filename: str = 'data/hh_vacancies.json') -> None:
        self.filename = filename

    def load_vacancies(self) -> List[Dict[str, Any]]:
        """Загрузка вакансий из JSON-файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

                if isinstance(data, dict) and 'items' in data:
                    data = data['items']
                    print("Найдены вакансии в поле 'items'")

                # Проверяем, что data - это список
                if not isinstance(data, list):
                    print(f"Данные не являются списком. Тип: {type(data)}")
                    return []

                print(f"Загружено {len(data)} вакансий из файла {self.filename}")
                return data

        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")
            return []
        except json.JSONDecodeError as e:
            print(f"Ошибка чтения JSON: {e}")
            return []
        except Exception as e:
            print(f"Ошибка: {e}")
            return []
