# lis_project/gui/pages/experiments_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ExperimentsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel("Все эксперименты")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #000000; margin: 10px;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Поиск по названию...")
        search_bar.setFixedWidth(250)
        search_bar.textChanged.connect(self.filter_table)
        top_layout.addWidget(search_bar)

        add_btn = QPushButton("Добавить эксперимент")
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

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Цель", "Статус", "Дата", "Исследователь"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.open_details)
        layout.addWidget(self.table)

        self.search_bar = search_bar
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        from database.crud import get_all_experiments_with_researchers
        data = get_all_experiments_with_researchers() or []
        self.table.setRowCount(len(data))
        for row, exp in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(exp['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(exp['name']))
            self.table.setItem(row, 2, QTableWidgetItem(exp['purpose']))
            self.table.setItem(row, 3, QTableWidgetItem(exp['status']))
            self.table.setItem(row, 4, QTableWidgetItem(exp['date']))
            self.table.setItem(row, 5, QTableWidgetItem(exp['researcher']))

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item:
                self.table.setRowHidden(row, text.lower() not in item.text().lower())

    def open_details(self, index):
        row = index.row()
        exp_id = int(self.table.item(row, 0).text())
        from database.crud import get_experiment_with_relations
        exp_data = get_experiment_with_relations(exp_id)
        if exp_data:  # ← ВАЖНО: двоеточие есть!
            from gui.dialogs.experiment_details_dialog import ExperimentDetailsDialog
            dialog = ExperimentDetailsDialog(exp_data, self)
            if dialog.exec():
                self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные эксперимента")

    def open_create_dialog(self):
        from gui.dialogs.create_experiment_dialog import CreateExperimentDialog
        dialog = CreateExperimentDialog(self)
        if dialog.exec():
            self.load_data()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
