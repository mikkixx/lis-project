# lis_project/gui/pages/my_experiments_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class MyExperimentsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()

        # === Верхняя панель ===
        top_layout = QHBoxLayout()
        title = QLabel("Мои эксперименты")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #000000; margin: 10px;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Поиск по названию...")
        search_bar.setFixedWidth(250)
        search_bar.textChanged.connect(self.filter_table)
        top_layout.addWidget(search_bar)

        # Кнопки действий
        add_btn = QPushButton("➕ Добавить")
        edit_btn = QPushButton("✏️ Редактировать")
        delete_btn = QPushButton("🗑️ Удалить")

        for btn in (add_btn, edit_btn, delete_btn):
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #000;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """)

        add_btn.clicked.connect(self.open_create_dialog)
        edit_btn.clicked.connect(self.edit_selected_experiment)
        delete_btn.clicked.connect(self.delete_selected_experiment)

        top_layout.addWidget(add_btn)
        top_layout.addWidget(edit_btn)
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        # === Разделитель ===
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)

        # === Таблица ===
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Цель", "Статус", "Дата"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.open_details) 
        layout.addWidget(self.table)

        self.search_bar = search_bar
        self.setLayout(layout)

    def load_data(self):
        from database.crud import get_my_experiments, get_current_researcher_id
        researcher_id = get_current_researcher_id()
        data = get_my_experiments(researcher_id) if researcher_id else []
        self.table.setRowCount(len(data))
        status_map = {'planned': 'Планирование', 'in_progress': 'В работе', 'completed': 'Завершен'}
        for row, exp in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(exp['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(exp['name']))
            self.table.setItem(row, 2, QTableWidgetItem(exp['purpose']))
            status_text = status_map.get(exp['status'], exp['status'])
            self.table.setItem(row, 3, QTableWidgetItem(status_text))
            self.table.setItem(row, 4, QTableWidgetItem(exp['date']))  # уже строка

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item:
                self.table.setRowHidden(row, text.lower() not in item.text().lower())

    def get_selected_experiment_id(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите эксперимент в таблице")
            return None
        row = selected[0].row()
        return int(self.table.item(row, 0).text())

    def open_create_dialog(self):
        from gui.dialogs.create_experiment_dialog import CreateExperimentDialog
        dialog = CreateExperimentDialog(self)
        if dialog.exec():
            self.load_data()

    def edit_selected_experiment(self):
        exp_id = self.get_selected_experiment_id()
        if exp_id is None:
            return

        from database.crud import get_experiment_by_id
        exp_obj = get_experiment_by_id(exp_id)
        if not exp_obj:
            QMessageBox.warning(self, "Ошибка", "Эксперимент не найден")
            return

        # Преобразуем в словарь
        exp_dict = {
            'id': exp_obj.id,
            'name': exp_obj.name,
            'purpose': exp_obj.purpose,
            'description': exp_obj.description,
            'plan': exp_obj.plan,
            'date_of_event': exp_obj.date_of_event.strftime('%Y-%m-%d') if exp_obj.date_of_event else '',
            'status': exp_obj.status
        }

        from gui.dialogs.edit_experiment_dialog import EditExperimentDialog
        dialog = EditExperimentDialog(exp_dict, self)
        if dialog.exec():
            self.load_data()

    def delete_selected_experiment(self):
        exp_id = self.get_selected_experiment_id()
        if exp_id is None:
            return

        exp_name = self.table.item(self.table.currentRow(), 1).text()
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить эксперимент «{exp_name}»?\nЭто действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import delete_experiment_completely
            if delete_experiment_completely(exp_id):
                QMessageBox.information(self, "Успех", "Эксперимент удалён")
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить эксперимент")
                
    def open_details(self, index):
        row = index.row()
        exp_id = int(self.table.item(row, 0).text())
        from database.crud import get_experiment_with_relations
        exp_data = get_experiment_with_relations(exp_id)
        if exp_data:
            from gui.dialogs.experiment_details_dialog import ExperimentDetailsDialog
            dialog = ExperimentDetailsDialog(exp_data, self)
            dialog.exec()  # ← только просмотр + управление

    def go_to_main(self):
        parent = self.parent()
        if parent and hasattr(parent, 'show_main'):
            parent.show_main()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
