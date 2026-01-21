from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                               QFrame, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from gui.dialogs.researcher_profile_dialog import ResearcherProfileDialog
from database.crud import get_all_researchers, delete_researcher

class ResearchersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel("Исследователи")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #000000; margin: 10px;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Поиск по фамилии...")
        search_bar.setFixedWidth(250)
        search_bar.textChanged.connect(self.filter_table)
        top_layout.addWidget(search_bar)

        layout.addLayout(top_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Фамилия", "Имя", "Организация"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.open_profile)
        layout.addWidget(self.table)

        self.search_bar = search_bar
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        from database.crud import get_all_researchers
        researchers = get_all_researchers()
        self.table.setRowCount(len(researchers))
        for row, r in enumerate(researchers):
            self.table.setItem(row, 0, QTableWidgetItem(str(r.id)))
            self.table.setItem(row, 1, QTableWidgetItem(r.surname))
            self.table.setItem(row, 2, QTableWidgetItem(r.name))
            self.table.setItem(row, 3, QTableWidgetItem(r.organization))

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            self.table.setRowHidden(row, text.lower() not in item.text().lower())

    def open_profile(self, index):
        row = index.row()
        researcher_id = int(self.table.item(row, 0).text())
        
        from database.crud import get_researcher_by_id
        researcher_obj = get_researcher_by_id(researcher_id)
        
        if not researcher_obj:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Исследователь не найден")
            return

        # ВСЕГДА только просмотр — даже для своего профиля
        researcher_data = {
            "id": researcher_obj.id,
            "surname": researcher_obj.surname,
            "name": researcher_obj.name,
            "patronymic": researcher_obj.patronymic,
            "biography": researcher_obj.biography,
            "academic_degree": researcher_obj.academic_degree,
            "organization": researcher_obj.organization,
            "email": researcher_obj.email,
            "URL": researcher_obj.URL
        }

        from gui.dialogs.researcher_profile_view_dialog import ResearcherProfileViewDialog
        dialog = ResearcherProfileViewDialog(researcher_data, self)
        dialog.exec()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
