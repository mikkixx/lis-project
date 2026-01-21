from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                               QFrame, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from gui.dialogs.sample_view_dialog import SampleViewDialog
from gui.dialogs.create_sample_dialog import CreateSampleDialog
from database.crud import get_all_samples, delete_sample

class SamplesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel("Образцы")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #000000; margin: 10px;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Поиск по названию...")
        search_bar.setFixedWidth(250)
        search_bar.textChanged.connect(self.filter_table)
        top_layout.addWidget(search_bar)

        add_btn = QPushButton("Добавить образец")
        add_btn.setFixedSize(180, 35)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        add_btn.clicked.connect(self.open_create_dialog)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Масса", "Объём", "Хим. формула"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.open_view)
        layout.addWidget(self.table)

        self.search_bar = search_bar
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        from database.crud import get_all_samples
        samples = get_all_samples()
        self.table.setRowCount(len(samples))
        for row, s in enumerate(samples):
            self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(row, 1, QTableWidgetItem(s.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(s.mass) if s.mass else ""))
            self.table.setItem(row, 3, QTableWidgetItem(str(s.volume) if s.volume else ""))
            self.table.setItem(row, 4, QTableWidgetItem(s.chemical_formula))

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            self.table.setRowHidden(row, text.lower() not in item.text().lower())

    def open_view(self, index):
        row = index.row()
        sample_id = int(self.table.item(row, 0).text())
        from database.crud import get_sample_by_id
        sample_obj = get_sample_by_id(sample_id)
        if sample_obj:
            # Преобразуем объект Peewee в словарь
            sample_dict = {
                'id': sample_obj.id,
                'name': sample_obj.name,
                'description': sample_obj.description,
                'chemical_formula': sample_obj.chemical_formula,
                'aggregate_state': sample_obj.aggregate_state,
                'mass': sample_obj.mass,
                'volume': sample_obj.volume
            }
            from gui.dialogs.sample_view_dialog import SampleViewDialog
            dialog = SampleViewDialog(sample_dict, self)  # ← передаём словарь, а не ID
            dialog.exec()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Образец не найден")

    def open_create_dialog(self):
        dialog = CreateSampleDialog(self)
        if dialog.exec():
            self.load_data()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
