from typing import Any, Dict, List, Optional

import requests


class HHApi:
    """Класс для работы с API hh.ru"""

    def __init__(self) -> None:
        self.base_url = "https://api.hh.ru"
        self.timeout: int = 10

        self.headers: Dict[str, str] = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://hh.ru/',
            'Accept': 'application/json'
        }

    def get_employer_vacancies(self, employer_name: str) -> List[Dict[str, Any]]:
        """Получение вакансий для конкретного работодателя"""
        params: Dict[str, Any] = {
            'text': f'company: {employer_name}',
            'area': 113,  # Россия
            'per_page': 10
        }

        try:
            response = requests.get(
                f"{self.base_url}/vacancies",
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            items: List[Dict[str, Any]] = data.get('items', [])
            return items
        except requests.RequestException as e:
            print(f"Ошибка при запросе вакансий: {e}")
            return []

    def get_vacancy_details(self, vacancy_id: str) -> Optional[Dict[str, Any]]:
        """Получение детальной информации о вакансии"""
        try:
            response = requests.get(
                f"{self.base_url}/vacancies/{vacancy_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except requests.RequestException:
            return None
