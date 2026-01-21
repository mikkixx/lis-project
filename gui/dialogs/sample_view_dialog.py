# lis_project/gui/dialogs/sample_view_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QPushButton, QTextEdit, QLineEdit
)
from PySide6.QtCore import Qt

class SampleViewDialog(QDialog):
    def __init__(self, sample_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр образца")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        form = QFormLayout()
        form.addRow("Название:", QLabel(sample_data.get("name", "")))
        form.addRow("Описание:", self._create_readonly_textedit(sample_data.get("description", "")))
        form.addRow("Химическая формула:", QLabel(sample_data.get("chemical_formula", "")))
        form.addRow("Агрегатное состояние:", QLabel(sample_data.get("aggregate_state", "")))
        form.addRow("Масса (г):", QLabel(str(sample_data.get("mass", ""))))
        form.addRow("Объем (см³):", QLabel(str(sample_data.get("volume", ""))))

        layout.addLayout(form)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def _create_readonly_textedit(self, text):
        te = QTextEdit()
        te.setPlainText(text)
        te.setReadOnly(True)
        te.setMaximumHeight(80)
        return te
