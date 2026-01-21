# lis_project/gui/dialogs/add_sample_to_experiment_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from database.crud import get_all_samples, add_sample_to_experiment

class AddSampleToExperimentDialog(QDialog):
    def __init__(self, experiment_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить образец к эксперименту")
        self.setFixedSize(400, 150)
        self.experiment_id = experiment_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Выберите образец:")
        layout.addWidget(label)

        self.sample_combo = QComboBox()
        samples = get_all_samples() or []
        for s in samples:
            self.sample_combo.addItem(f"{s.name} (ID: {s.id})", s.id)
        layout.addWidget(self.sample_combo)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        cancel_btn = QPushButton("Отмена")

        add_btn.clicked.connect(self.add_sample)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_sample(self):
        sample_id = self.sample_combo.currentData()
        if sample_id is None:
            QMessageBox.warning(self, "Ошибка", "Не выбран образец")
            return
        if add_sample_to_experiment(self.experiment_id, sample_id):
            QMessageBox.information(self, "Успех", "Образец добавлен к эксперименту")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить образец")
