import os
import sys

from PyQt6.QtWidgets import QApplication

from character import Character
from command_manager import CommandManager
from tray_icon import TrayIcon
from windows import CreateCommandWindow, RunCommandWindow


def main():
    """Запускает десктопного помощника."""
    # работаем из папки проекта, чтобы находились картинки и json-файлы
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    app = QApplication(sys.argv)
    # не закрывать программу, когда персонаж спрятан в трей
    app.setQuitOnLastWindowClosed(False)

    manager = CommandManager()
    character = Character()
    tray = TrayIcon(character, character.image_path)

    # связываем сигналы персонажа с окнами и треем
    character.create_command_requested.connect(
        lambda: CreateCommandWindow(manager, character).exec())
    character.run_command_requested.connect(
        lambda: RunCommandWindow(manager, character).exec())
    character.hide_requested.connect(tray.hide_character)
    character.quit_requested.connect(tray.quit_app)

    character.show()
    tray.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
