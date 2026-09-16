"""
Модуль для работы с JSON файлами.
Демонстрирует работу с файловым вводом-выводом и JSON сериализацией.
"""
import json
from pathlib import Path
from typing import Any


class JsonHandler:
    """Класс для работы с JSON файлами."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def read_json(self) -> dict[str, Any]:
        """
        Прочитать данные из JSON файла.

        Returns:
            dict: Распарсенные данные из JSON

        Raises:
            FileNotFoundError: Если файл не найден
            json.JSONDecodeError: Если JSON невалидный
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл {self.file_path} не найден")

        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_json(self, data: dict[str, Any], indent: int = 2) -> None:
        """
        Записать данные в JSON файл.

        Args:
            data: Данные для записи
            indent: Количество пробелов для форматирования

        Raises:
            IOError: Если не удалось записать файл
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=indent)

    def append_to_list(self, key: str, item: dict[str, Any]) -> None:
        """
        Добавить элемент в список внутри JSON.

        Args:
            key: Ключ списка в JSON
            item: Элемент для добавления
        """
        data = self.read_json()

        if key not in data:
            data[key] = []

        if not isinstance(data[key], list):
            raise ValueError(f"Ключ '{key}' не является списком")

        data[key].append(item)
        self.write_json(data)

    def find_by_id(self, key: str, item_id: int) -> dict[str, Any] | None:
        """
        Найти элемент по ID в списке.

        Args:
            key: Ключ списка в JSON
            item_id: ID элемента

        Returns:
            dict | None: Найденный элемент или None
        """
        data = self.read_json()

        if key not in data or not isinstance(data[key], list):
            return None

        for item in data[key]:
            if isinstance(item, dict) and item.get('id') == item_id:
                return item

        return None

    def filter_by_field(self, key: str, field: str, value: Any) -> list[dict[str, Any]]:
        """
        Фильтровать элементы по значению поля.

        Args:
            key: Ключ списка в JSON
            field: Название поля
            value: Значение для фильтрации

        Returns:
            list: Отфильтрованные элементы
        """
        data = self.read_json()

        if key not in data or not isinstance(data[key], list):
            return []

        return [
            item for item in data[key]
            if isinstance(item, dict) and item.get(field) == value
        ]

    def __str__(self) -> str:
        """Строковое представление."""
        return f"JsonHandler(file_path='{self.file_path}')"

    def __repr__(self) -> str:
        """Строковое представление для разработчика."""
        return f"JsonHandler(file_path='{self.file_path}')"
