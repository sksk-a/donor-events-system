from datetime import datetime,date
from enum import Enum
from typing import TypeVar

E=TypeVar("E",bound=Enum)


class InputUtils:
    @staticmethod
    def read_non_empty(prompt:str,default:str|None=None)->str:
        while True:
            value=input(prompt).strip()
            if value:return value
            if default is not None:return default
            print("Значение не может быть пустым.")
    @staticmethod
    def read_int(prompt:str,minimum:int|None=None,default:int|None=None)->int:
        while True:
            raw=input(prompt).strip()
            if not raw and default is not None:return default
            try:
                value=int(raw)
                if minimum is not None and value<minimum:raise ValueError
                return value
            except ValueError:print("Введите корректное целое число.")
    @staticmethod
    def read_date(prompt:str,default:date|None=None)->date:
        while True:
            raw=input(prompt).strip()
            if not raw and default:return default
            try:return datetime.strptime(raw,"%Y-%m-%d").date()
            except ValueError:print("Дата должна иметь формат YYYY-MM-DD.")
    @staticmethod
    def read_enum(prompt:str,enum_type:type[E],default:E|None=None)->E:
        choices=", ".join(x.value for x in enum_type)
        while True:
            raw=input(f"{prompt} ({choices}): ").strip().upper()
            if not raw and default:return default
            try:return enum_type(raw)
            except ValueError:print("Выберите одно из допустимых значений.")
