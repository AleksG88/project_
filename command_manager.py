"""Менеджер команд: хранит список команд и сохраняет их в файл."""

import json

from command import Command


class CommandManager:
    """Управляет списком команд помощника."""

    def __init__(self, file_path="commands.json"):
        self.commands = []            # список объектов Command
        self.file_path = file_path    # файл, где хранятся команды
        self.load()

    def add_command(self, command):
        """Добавляет команду и сразу сохраняет список в файл."""
        self.commands.append(command)
        self.save()

    def remove_command(self, name):
        """Удаляет команду по названию и сохраняет список."""
        self.commands = [c for c in self.commands if c.name != name]
        self.save()

    def get_commands(self):
        """Возвращает список всех команд."""
        return self.commands

    def run_command(self, name):
        """Находит команду по названию и выполняет её."""
        for command in self.commands:
            if command.name == name:
                command.execute()
                return
        raise ValueError(f"Команда не найдена: {name}")

    def save(self):
        """Сохраняет все команды в файл в формате JSON."""
        data = [c.to_dict() for c in self.commands]
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def load(self):
        """Загружает команды из файла, если он есть."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.commands = [Command.from_dict(item) for item in data]
        except FileNotFoundError:
            self.commands = []


if __name__ == "__main__":
    # быстрая проверка: добавим команду и выведем список
    from command import CommandType

    manager = CommandManager()
    manager.add_command(Command("Открыть документы", CommandType.OPEN_FOLDER,
                                "C:\\"))
    for cmd in manager.get_commands():
        print(cmd.name, "-", cmd.command_type.value, "-", cmd.options)
        