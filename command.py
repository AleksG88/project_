"""Команда помощника: название, тип и опции."""

import os
import subprocess
from enum import Enum


class CommandType(Enum):
    """Типы команд, которые умеет выполнять помощник."""

    OPEN_FOLDER = "Открыть папку"
    OPEN_FILE = "Открыть файл"
    SHUTDOWN = "Выключить компьютер"


class Command:
    """Одна команда помощника."""

    def __init__(self, name, command_type, options=""):
        self.name = name                  # название команды
        self.command_type = command_type  # тип из CommandType
        self.options = options            # путь к папке или файлу

    def execute(self):
        """Выполняет команду в зависимости от её типа."""
        if self.command_type in (CommandType.OPEN_FOLDER,
                                 CommandType.OPEN_FILE):
            if not os.path.exists(self.options):
                raise FileNotFoundError(f"Путь не найден: {self.options}")
            os.startfile(self.options)
        elif self.command_type == CommandType.SHUTDOWN:
            # выключение через 30 секунд, отменить: shutdown /a
            subprocess.run(["shutdown", "/s", "/t", "30"], check=False)

    def to_dict(self):
        """Превращает команду в словарь для сохранения в файл."""
        return {
            "name": self.name,
            "type": self.command_type.name,
            "options": self.options,
        }

    @staticmethod
    def from_dict(data):
        """Создаёт команду из словаря, прочитанного из файла."""
        return Command(data["name"], CommandType[data["type"]],
                       data.get("options", ""))


if __name__ == "__main__":
    # быстрая проверка: откроет папку проекта
    Command("Тест", CommandType.OPEN_FOLDER, os.getcwd()).execute()