# lis_project/gui/pages/my_samples_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class MySamplesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel("Мои образцы")
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
        edit_btn.clicked.connect(self.edit_selected_sample)
        delete_btn.clicked.connect(self.delete_selected_sample)

        top_layout.addWidget(add_btn)
        top_layout.addWidget(edit_btn)
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)

        # СОЗДАЁМ ТАБЛИЦУ
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Масса", "Объём", "Хим. формула"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # ПОДКЛЮЧАЕМ СИГНАЛ ПОСЛЕ СОЗДАНИЯ
        self.table.doubleClicked.connect(self.open_view)  # ← Теперь безопасно!

        layout.addWidget(self.table)

        self.search_bar = search_bar
        self.setLayout(layout)

    def load_data(self):
        from database.crud import get_my_samples, get_current_researcher_id
        researcher_id = get_current_researcher_id()
        samples = get_my_samples(researcher_id) if researcher_id else []
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
            if item:
                self.table.setRowHidden(row, text.lower() not in item.text().lower())

    def get_selected_sample_id(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите образец в таблице")
            return None
        row = selected[0].row()
        return int(self.table.item(row, 0).text())

    def open_view(self, index):
        """Открывает окно ПРОСМОТРА при двойном клике"""
        row = index.row()
        sample_id = int(self.table.item(row, 0).text())
        from database.crud import get_sample_by_id
        sample_obj = get_sample_by_id(sample_id)
        if not sample_obj:
            QMessageBox.warning(self, "Ошибка", "Образец не найден")
            return

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
        dialog = SampleViewDialog(sample_dict, self)
        dialog.exec()

    def open_create_dialog(self):
        from gui.dialogs.create_sample_dialog import CreateSampleDialog
        dialog = CreateSampleDialog(self)
        if dialog.exec():
            self.load_data()

    def edit_selected_sample(self):
        """Редактирование через кнопку (не через двойной клик)"""
        sample_id = self.get_selected_sample_id()
        if sample_id is None:
            return

        from database.crud import get_sample_by_id
        sample_obj = get_sample_by_id(sample_id)
        if not sample_obj:
            QMessageBox.warning(self, "Ошибка", "Образец не найден")
            return

        sample_dict = {
            'id': sample_obj.id,
            'name': sample_obj.name,
            'description': sample_obj.description,
            'chemical_formula': sample_obj.chemical_formula,
            'aggregate_state': sample_obj.aggregate_state,
            'mass': sample_obj.mass,
            'volume': sample_obj.volume
        }

        from gui.dialogs.edit_sample_dialog import EditSampleDialog
        dialog = EditSampleDialog(sample_dict, self)
        if dialog.exec():
            self.load_data()

    def delete_selected_sample(self):
        sample_id = self.get_selected_sample_id()
        if sample_id is None:
            return

        sample_name = self.table.item(self.table.currentRow(), 1).text()
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить образец «{sample_name}»?\nЭто действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import delete_sample_completely
            if delete_sample_completely(sample_id):
                QMessageBox.information(self, "Успех", "Образец удалён")
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить образец")

    def go_to_main(self):
        parent = self.parent()
        if parent and hasattr(parent, 'show_main'):
            parent.show_main()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
