"""Персонаж помощника: окно без рамки с картинкой и именем."""

import json
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QApplication, QFileDialog, QInputDialog,
                             QLabel, QLineEdit, QMenu, QVBoxLayout,
                             QWidget)

DEFAULT_NAME = "Рик Сначес"
DEFAULT_IMAGE = "images/rick.png"
SETTINGS_FILE = "settings.json"
IMAGE_SIZE = 200


class Character(QWidget):
    """Окно без рамки, в котором виден персонаж помощника."""

    # сигналы: персонаж сообщает программе, что выбрал пользователь
    create_command_requested = pyqtSignal()
    run_command_requested = pyqtSignal()
    hide_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.name = DEFAULT_NAME
        self.image_path = DEFAULT_IMAGE
        self.drag_offset = None
        self.load_settings()

        # окно без рамки, поверх других окон, без значка на панели задач
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.image_label = QLabel()
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFixedWidth(IMAGE_SIZE)
        self.name_label.setStyleSheet(
            "color: white; background: rgba(0, 0, 0, 160);"
            "border-radius: 8px; padding: 4px; font-size: 13px;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        self.update_view()

    def update_view(self):
        """Показывает текущую картинку и имя."""
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            pixmap = QPixmap(DEFAULT_IMAGE)
        if pixmap.isNull():
            self.image_label.setText("Картинка не найдена")
        else:
            self.image_label.setPixmap(pixmap.scaled(
                IMAGE_SIZE, IMAGE_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        self.name_label.setText(f"{self.name}, твой персональный помощник")
        self.adjustSize()

    def change_image(self):
        """Открывает выбор файла и ставит новую картинку."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите картинку", "",
            "Изображения (*.png *.jpg *.jpeg *.gif)")
        if path:
            self.image_path = path
            self.save_settings()
            self.update_view()

    def change_name(self, new_name=None):
        """Меняет имя помощника (если имя не передано, спрашивает)."""
        if new_name is None:
            new_name, ok = QInputDialog.getText(
                self, "Имя помощника", "Введите новое имя:",
                QLineEdit.EchoMode.Normal, self.name)
            if not ok:
                return
        new_name = new_name.strip()
        if new_name:
            self.name = new_name
            self.save_settings()
            self.update_view()

    def show_menu(self, position):
        """Показывает меню помощника в указанной точке экрана."""
        menu = QMenu(self)
        menu.addAction("Выполнить команду").triggered.connect(
            lambda: self.run_command_requested.emit())
        menu.addAction("Создать команду").triggered.connect(
            lambda: self.create_command_requested.emit())
        menu.addSeparator()
        menu.addAction("Сменить картинку").triggered.connect(
            lambda: self.change_image())
        menu.addAction("Сменить имя").triggered.connect(
            lambda: self.change_name())
        menu.addSeparator()
        menu.addAction("Свернуть в трей").triggered.connect(
            lambda: self.hide_requested.emit())
        menu.addAction("Выход").triggered.connect(
            lambda: self.quit_requested.emit())
        menu.exec(position)

    def contextMenuEvent(self, event):
        """Правый клик по персонажу открывает меню."""
        self.show_menu(event.globalPos())

    def mousePressEvent(self, event):
        """Запоминает точку, за которую схватили персонажа."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = (event.globalPosition().toPoint()
                                - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        """Перетаскивает персонажа мышкой."""
        if (self.drag_offset is not None
                and event.buttons() & Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        """Заканчивает перетаскивание."""
        self.drag_offset = None

    def load_settings(self):
        """Загружает имя и картинку из файла настроек."""
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.name = data.get("name", DEFAULT_NAME)
            self.image_path = data.get("image_path", DEFAULT_IMAGE)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_settings(self):
        """Сохраняет имя и картинку в файл настроек."""
        data = {"name": self.name, "image_path": self.image_path}
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # быстрая проверка: показать персонажа
    app = QApplication(sys.argv)
    character = Character()
    character.quit_requested.connect(app.quit)
    character.show()
    sys.exit(app.exec())
    