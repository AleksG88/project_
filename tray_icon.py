"""Значок помощника в системном трее."""

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    """Значок в трее: показывает и прячет персонажа, закрывает программу."""

    def __init__(self, character, icon_path, parent=None):
        super().__init__(QIcon(icon_path), parent)
        self.character = character
        self.setToolTip("Десктопный помощник")

        self.menu = QMenu()
        self.menu.addAction("Показать помощника").triggered.connect(
            lambda: self.show_character())
        self.menu.addAction("Скрыть помощника").triggered.connect(
            lambda: self.hide_character())
        self.menu.addSeparator()
        self.menu.addAction("Выход").triggered.connect(
            lambda: self.quit_app())
        self.setContextMenu(self.menu)

        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        """Левый клик по значку показывает или прячет персонажа."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.character.isVisible():
                self.hide_character()
            else:
                self.show_character()

    def show_character(self):
        """Показывает персонажа на рабочем столе."""
        self.character.show()
        self.character.raise_()
        self.character.activateWindow()

    def hide_character(self):
        """Прячет персонажа в трей."""
        self.character.hide()
        self.showMessage(self.character.name,
                         "Я здесь, в трее. Кликни по значку, чтобы вернуть.")

    def quit_app(self):
        """Закрывает программу."""
        self.hide()
        QApplication.quit()
