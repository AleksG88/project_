"""Окна помощника: создание команды и выполнение команды."""

import os
import sys

from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog,
                             QFileDialog, QFormLayout, QHBoxLayout,
                             QLineEdit, QListWidget, QMessageBox,
                             QPushButton, QVBoxLayout)

from command import Command, CommandType
from command_manager import CommandManager


class CreateCommandWindow(QDialog):
    """Окно, в котором пользователь создаёт новую команду."""

    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Создание команды")
        self.setMinimumWidth(400)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: Открыть курсовую")

        self.type_box = QComboBox()
        for command_type in CommandType:
            self.type_box.addItem(command_type.value, command_type)
        self.type_box.currentIndexChanged.connect(self.on_type_changed)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Путь к папке или файлу")
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)

        form = QFormLayout()
        form.addRow("Название:", self.name_edit)
        form.addRow("Тип команды:", self.type_box)
        form.addRow("Путь:", path_layout)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_command)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def current_type(self):
        """Возвращает выбранный тип команды."""
        return self.type_box.currentData()

    def on_type_changed(self):
        """Для выключения компьютера путь не нужен — блокируем поле."""
        need_path = self.current_type() != CommandType.SHUTDOWN
        self.path_edit.setEnabled(need_path)
        self.browse_button.setEnabled(need_path)

    def browse(self):
        """Открывает выбор папки или файла в зависимости от типа."""
        if self.current_type() == CommandType.OPEN_FOLDER:
            path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if path:
            self.path_edit.setText(os.path.normpath(path))

    def save_command(self):
        """Проверяет введённые данные и сохраняет команду."""
        name = self.name_edit.text().strip()
        command_type = self.current_type()
        path = self.path_edit.text().strip()

        if not name:
            self.show_error("Введите название команды.")
            return
        if any(c.name == name for c in self.manager.get_commands()):
            self.show_error("Команда с таким названием уже есть.")
            return
        if command_type == CommandType.SHUTDOWN:
            path = ""
        elif not os.path.exists(path):
            self.show_error("Укажите существующую папку или файл.")
            return

        self.manager.add_command(Command(name, command_type, path))
        self.accept()

    def show_error(self, text):
        """Показывает окно с ошибкой."""
        QMessageBox.warning(self, "Ошибка", text)


class RunCommandWindow(QDialog):
    """Окно со списком команд, из которого их можно выполнить."""

    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Выполнение команды")
        self.setMinimumSize(400, 300)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.run_selected)

        run_button = QPushButton("Выполнить")
        run_button.clicked.connect(self.run_selected)
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_selected)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(run_button)
        buttons.addWidget(delete_button)
        buttons.addStretch()
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self):
        """Заново заполняет список команд."""
        self.list_widget.clear()
        for command in self.manager.get_commands():
            self.list_widget.addItem(
                f"{command.name}  ({command.command_type.value})")

    def selected_command(self):
        """Возвращает выбранную в списке команду или None."""
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Подсказка",
                                    "Сначала выберите команду в списке.")
            return None
        return self.manager.get_commands()[row]

    def run_selected(self):
        """Выполняет выбранную команду."""
        command = self.selected_command()
        if command is None:
            return
        if command.command_type == CommandType.SHUTDOWN:
            answer = QMessageBox.question(
                self, "Подтверждение",
                "Выключить компьютер через 30 секунд?")
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            self.manager.run_command(command.name)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось выполнить команду:\n{error}")
            return
        QMessageBox.information(self, "Готово",
                                f"Команда «{command.name}» выполнена.")

    def delete_selected(self):
        """Удаляет выбранную команду после подтверждения."""
        command = self.selected_command()
        if command is None:
            return
        answer = QMessageBox.question(
            self, "Удаление", f"Удалить команду «{command.name}»?")
        if answer == QMessageBox.StandardButton.Yes:
            self.manager.remove_command(command.name)
            self.refresh()


if __name__ == "__main__":
    # быстрая проверка: сначала окно создания, потом окно выполнения
    app = QApplication(sys.argv)
    test_manager = CommandManager()
    CreateCommandWindow(test_manager).exec()
    RunCommandWindow(test_manager).exec()
    