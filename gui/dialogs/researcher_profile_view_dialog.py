# lis_project/gui/dialogs/researcher_profile_view_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QPushButton,
    QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ResearcherProfileViewDialog(QDialog):
    def __init__(self, researcher_data, parent=None):
        super().__init__(parent)
        self.researcher_data = researcher_data
        self.parent_window = parent
        self.setWindowTitle("Профиль исследователя")
        self.setFixedSize(500, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Профиль исследователя")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Форма с данными
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Поля
        fields = [
            ("Фамилия", self.researcher_data.get("surname", "")),
            ("Имя", self.researcher_data.get("name", "")),
            ("Отчество", self.researcher_data.get("patronymic", "")),
            ("Ученая степень", self.researcher_data.get("academic_degree", "")),
            ("Организация", self.researcher_data.get("organization", "")),
            ("Email", self.researcher_data.get("email", "")),
            ("URL соц сети", self.researcher_data.get("URL", ""))
        ]

        for label_text, value in fields:
            if label_text == "Биография":
                continue  # обработаем отдельно
            label = QLabel(value)
            label.setStyleSheet("color: #000; background-color: #f9f9f9; padding: 4px;")
            label.setWordWrap(True)
            form.addRow(f"<b>{label_text}:</b>", label)

        # Биография — многострочное поле
        bio_label = QLabel("<b>Биография:</b>")
        form.addRow(bio_label)
        bio_text = QTextEdit()
        bio_text.setPlainText(self.researcher_data.get("biography", ""))
        bio_text.setReadOnly(True)
        bio_text.setMaximumHeight(100)
        form.addRow(bio_text)

        layout.addLayout(form)

        # Кнопки
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")

        close_btn.setFixedHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
        """)

        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def edit_profile(self):
        from .profile_dialog import ProfileDialog
        # Передаём ID исследователя (предполагаем, что он есть в данных)
        researcher_id = self.researcher_data.get("id", 1)
        dialog = ProfileDialog(researcher_id, self.parent_window)
        if dialog.exec():
            # После сохранения — можно обновить данные (опционально)
            pass
        self.accept()  # Закрываем просмотр после редактирования
