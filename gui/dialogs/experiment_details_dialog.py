# lis_project/gui/dialogs/experiment_details_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ExperimentDetailsDialog(QDialog):
    def __init__(self, experiment_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Детали эксперимента")
        self.setFixedSize(1000, 700)
        self.experiment_data = experiment_data
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        exp = self.experiment_data['experiment']
        researchers = self.experiment_data['researchers']

        # Заголовок
        title = QLabel(f"Эксперимент: {exp.name}")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Основная информация
        status_rus = {
            'planned': 'Планирование',
            'in_progress': 'В работе',
            'completed': 'Завершён'
        }.get(exp.status, exp.status)
        date_str = exp.date_of_event.strftime('%d.%m.%Y') if exp.date_of_event else 'Не указана'
        researcher_names = ', '.join([f"{r.surname} {r.name}" for r in researchers])

        info_text = f"""
        <b>Цель:</b> {exp.purpose}<br/>
        <b>Статус:</b> {status_rus}<br/>
        <b>Дата:</b> {date_str}<br/>
        <b>Исследователь:</b> {researcher_names}
        """
        info_label = QLabel(info_text)
        info_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 8px;")
        layout.addWidget(info_label)

        # Вкладки
        tabs = QTabWidget()
        tabs.addTab(self.create_text_tab(exp.description or "Описание отсутствует"), "Описание")
        tabs.addTab(self.create_text_tab(exp.plan or "План отсутствует"), "План")

        # === МЕТОДЫ (с кнопками, если свой эксперимент) ===
        methods_widget = self.create_methods_tab()
        tabs.addTab(methods_widget, "Методы")

        tabs.addTab(self.create_samples_tab(), "Образцы")
        tabs.addTab(self.create_equipment_tab(), "Оборудование")
        tabs.addTab(self.create_measurements_tab(), "Измерения")
        tabs.addTab(self.create_conditions_tab(), "Условия")
        tabs.addTab(self.create_results_tab(), "Результаты")
        layout.addWidget(tabs)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setFixedHeight(35)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def is_my_experiment(self):
        """Проверяет, принадлежит ли эксперимент текущему пользователю (id=1)"""
        MY_USER_ID = 1
        researchers = self.experiment_data.get('researchers', [])
        return any(r.id == MY_USER_ID for r in researchers)

    def create_methods_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Таблица методов
        methods = self.experiment_data['methods']
        table = QTableWidget(len(methods), 3)
        table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, method in enumerate(methods):
            table.setItem(row, 0, QTableWidgetItem(str(method.id)))
            table.setItem(row, 1, QTableWidgetItem(method.name))
            table.setItem(row, 2, QTableWidgetItem(method.description))

        layout.addWidget(table)
        self.methods_table = table

        # Кнопки управления — только для своего эксперимента
        if self.is_my_experiment():
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("➕ Добавить")
            edit_btn = QPushButton("✏️ Редактировать")
            delete_btn = QPushButton("🗑️ Удалить")

            for btn in [add_btn, edit_btn, delete_btn]:
                btn.setFixedHeight(30)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #333;
                    }
                """)

            add_btn.clicked.connect(self.add_method)
            edit_btn.clicked.connect(self.edit_method)
            delete_btn.clicked.connect(self.delete_method)

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            layout.addLayout(btn_layout)

        return widget

    def get_selected_method_id(self):
        selected = self.methods_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите метод в таблице")
            return None
        row = selected[0].row()
        return int(self.methods_table.item(row, 0).text())

    def add_method(self):
        from gui.dialogs.add_method_dialog import AddMethodDialog
        exp_id = self.experiment_data['experiment'].id
        dialog = AddMethodDialog(exp_id, self)
        if dialog.exec():
            self.reload_experiment_data()

    def edit_method(self):
        method_id = self.get_selected_method_id()
        if not method_id:
            return
        from database.crud import get_method_by_id
        method_obj = get_method_by_id(method_id)
        if not method_obj:
            QMessageBox.warning(self, "Ошибка", "Метод не найден")
            return
        from gui.dialogs.edit_method_dialog import EditMethodDialog
        dialog = EditMethodDialog({
            'id': method_obj.id,
            'name': method_obj.name,
            'description': method_obj.description
        }, self)
        if dialog.exec():
            self.reload_experiment_data()

    def delete_method(self):
        method_id = self.get_selected_method_id()
        if not method_id:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот метод?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import delete_method
            if delete_method(method_id):
                QMessageBox.information(self, "Успех", "Метод удалён")
                self.reload_experiment_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить метод")

    def reload_experiment_data(self):
        """Перезагружает данные эксперимента и обновляет интерфейс"""
        from database.crud import get_experiment_with_relations
        exp_id = self.experiment_data['experiment'].id
        self.experiment_data = get_experiment_with_relations(exp_id)
        self.init_ui()  # ← перестраиваем весь диалог

    def create_text_tab(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        return widget
        
    def create_samples_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        samples = self.experiment_data['samples']
        
        # ВСЕГДА создаём таблицу (даже если данных нет)
        table = QTableWidget(len(samples), 5)
        table.setHorizontalHeaderLabels(["ID", "Название", "Формула", "Состояние", "Масса"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("samples_table")  # ← Теперь безопасно!

        for row, sample in enumerate(samples):
            if sample is None:
                continue
            table.setItem(row, 0, QTableWidgetItem(str(sample.id)))
            table.setItem(row, 1, QTableWidgetItem(sample.name))
            table.setItem(row, 2, QTableWidgetItem(sample.chemical_formula))
            table.setItem(row, 3, QTableWidgetItem(sample.aggregate_state))
            table.setItem(row, 4, QTableWidgetItem(str(sample.mass)))

        layout.addWidget(table)

        # Кнопки управления — только для своего эксперимента
        if self.is_my_experiment():
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("➕ Добавить")
            edit_btn = QPushButton("✏️ Редактировать")
            delete_btn = QPushButton("🗑️ Удалить")

            for btn in [add_btn, edit_btn, delete_btn]:
                btn.setFixedHeight(30)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #333;
                    }
                """)

            add_btn.clicked.connect(self.add_sample_to_experiment)
            edit_btn.clicked.connect(self.edit_selected_sample)
            delete_btn.clicked.connect(self.remove_sample_from_experiment)

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            layout.addLayout(btn_layout)

        return widget
        
    def get_selected_sample_id(self):
        table = self.findChild(QTableWidget, "samples_table")
        if not table:
            QMessageBox.warning(self, "Ошибка", "Таблица образцов недоступна")
            return None
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите образец в таблице")
            return None
        row = selected[0].row()
        return int(table.item(row, 0).text())

    def add_sample_to_experiment(self):
        from gui.dialogs.add_sample_to_experiment_dialog import AddSampleToExperimentDialog
        exp_id = self.experiment_data['experiment'].id
        dialog = AddSampleToExperimentDialog(exp_id, self)
        if dialog.exec():
            self.reload_experiment_data()

    def edit_selected_sample(self):
        sample_id = self.get_selected_sample_id()
        if not sample_id:
            return
        from database.crud import get_sample_by_id
        sample_obj = get_sample_by_id(sample_id)
        if not sample_obj:
            QMessageBox.warning(self, "Ошибка", "Образец не найден")
            return
        from gui.dialogs.edit_sample_dialog import EditSampleDialog
        sample_dict = {
            'id': sample_obj.id,
            'name': sample_obj.name,
            'description': sample_obj.description,
            'chemical_formula': sample_obj.chemical_formula,
            'aggregate_state': sample_obj.aggregate_state,
            'mass': sample_obj.mass,
            'volume': sample_obj.volume
        }
        dialog = EditSampleDialog(sample_dict, self)
        if dialog.exec():
            self.reload_experiment_data()

    def remove_sample_from_experiment(self):
        sample_id = self.get_selected_sample_id()
        if not sample_id:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот образец из эксперимента?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import remove_sample_from_experiment
            if remove_sample_from_experiment(self.experiment_data['experiment'].id, sample_id):
                QMessageBox.information(self, "Успех", "Образец удалён из эксперимента")
                self.reload_experiment_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить образец")
                
    def create_equipment_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        equipment_list = self.experiment_data['equipment']
        
        # ВСЕГДА создаём таблицу (даже если данных нет)
        table = QTableWidget(len(equipment_list), 3)
        table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("equipment_table")  # ← Теперь безопасно!

        for row, equip in enumerate(equipment_list):
            if equip is None:
                continue
            table.setItem(row, 0, QTableWidgetItem(str(equip.id)))
            table.setItem(row, 1, QTableWidgetItem(equip.name))
            table.setItem(row, 2, QTableWidgetItem(equip.description))

        layout.addWidget(table)

        # Кнопки управления — только для своего эксперимента
        if self.is_my_experiment():
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("➕ Добавить")
            edit_btn = QPushButton("✏️ Редактировать")
            delete_btn = QPushButton("🗑️ Удалить")

            for btn in [add_btn, edit_btn, delete_btn]:
                btn.setFixedHeight(30)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #333;
                    }
                """)

            add_btn.clicked.connect(self.add_equipment_to_experiment)
            edit_btn.clicked.connect(self.edit_selected_equipment)
            delete_btn.clicked.connect(self.remove_equipment_from_experiment)

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            layout.addLayout(btn_layout)

        return widget
        
    def get_selected_equipment_id(self):
        table = self.findChild(QTableWidget, "equipment_table")
        if not table:
            QMessageBox.warning(self, "Ошибка", "Таблица оборудования недоступна")
            return None
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите оборудование в таблице")
            return None
        row = selected[0].row()
        return int(table.item(row, 0).text())

    def add_equipment_to_experiment(self):
        from gui.dialogs.add_equipment_dialog import AddEquipmentDialog
        exp_id = self.experiment_data['experiment'].id
        dialog = AddEquipmentDialog(exp_id, self)
        if dialog.exec():
            self.reload_experiment_data()

    def edit_selected_equipment(self):
        equip_id = self.get_selected_equipment_id()
        if not equip_id:
            return
        from database.crud import get_equipment_by_id
        equip_obj = get_equipment_by_id(equip_id)
        if not equip_obj:
            QMessageBox.warning(self, "Ошибка", "Оборудование не найдено")
            return
        from gui.dialogs.edit_equipment_dialog import EditEquipmentDialog
        dialog = EditEquipmentDialog({
            'id': equip_obj.id,
            'name': equip_obj.name,
            'description': equip_obj.description
        }, self)
        if dialog.exec():
            self.reload_experiment_data()

    def remove_equipment_from_experiment(self):
        equip_id = self.get_selected_equipment_id()
        if not equip_id:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить это оборудование из эксперимента?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import remove_equipment_from_experiment
            if remove_equipment_from_experiment(self.experiment_data['experiment'].id, equip_id):
                QMessageBox.information(self, "Успех", "Оборудование удалено из эксперимента")
                self.reload_experiment_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить оборудование")
                
    def create_measurements_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        measurements = self.experiment_data['measurements']
        
        # Всегда создаём таблицу (даже если данных нет)
        table = QTableWidget(len(measurements), 8)
        table.setHorizontalHeaderLabels(["ID", "Образец", "Метод", "Параметр", "Значение", "Ед.", "Точность", "Время"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("measurements_table")  # ← Теперь безопасно!

        for row, m in enumerate(measurements):
            if m is None:
                continue

            sample_name = m.sample.name if m.sample else "—"
            
            # Обработка времени
            time_str = "—"
            if m.time_of_event:
                if isinstance(m.time_of_event, str):
                    if m.time_of_event.startswith("0000-00-00") or m.time_of_event == "0000-00-00 00:00:00":
                        time_str = "—"
                    else:
                        try:
                            from datetime import datetime
                            dt = datetime.strptime(m.time_of_event, '%Y-%m-%d %H:%M:%S')
                            time_str = dt.strftime('%d.%m.%Y %H:%M')
                        except ValueError:
                            time_str = "—"
                else:
                    time_str = m.time_of_event.strftime('%d.%m.%Y %H:%M')

            table.setItem(row, 0, QTableWidgetItem(str(m.id)))
            table.setItem(row, 1, QTableWidgetItem(sample_name))
            table.setItem(row, 2, QTableWidgetItem(m.method))
            table.setItem(row, 3, QTableWidgetItem(m.property))  # ← ПАРАМЕТР
            table.setItem(row, 4, QTableWidgetItem(str(m.value)))
            table.setItem(row, 5, QTableWidgetItem(m.unit))
            table.setItem(row, 6, QTableWidgetItem(str(m.accuracy)))
            table.setItem(row, 7, QTableWidgetItem(time_str))

        layout.addWidget(table)

        # Кнопки управления (если свой эксперимент)
        if self.is_my_experiment():
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("➕ Добавить")
            edit_btn = QPushButton("✏️ Редактировать")
            delete_btn = QPushButton("🗑️ Удалить")

            for btn in [add_btn, edit_btn, delete_btn]:
                btn.setFixedHeight(30)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #333;
                    }
                """)

            add_btn.clicked.connect(self.add_measurement)
            edit_btn.clicked.connect(self.edit_selected_measurement)
            delete_btn.clicked.connect(self.delete_selected_measurement)

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            layout.addLayout(btn_layout)

        return widget
    
    def get_selected_measurement_id(self):
        # Находим таблицу по имени
        table = self.findChild(QTableWidget, "measurements_table")
        if not table:
            QMessageBox.warning(self, "Ошибка", "Таблица недоступна")
            return None
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите измерение в таблице")
            return None
        row = selected[0].row()
        return int(table.item(row, 0).text())

    def add_measurement(self):
        from gui.dialogs.add_measurement_dialog import AddMeasurementDialog
        exp_id = self.experiment_data['experiment'].id
        dialog = AddMeasurementDialog(exp_id, self)
        if dialog.exec():
            self.reload_experiment_data()

    def edit_selected_measurement(self):
        measurement_id = self.get_selected_measurement_id()
        if not measurement_id:
            return
        from database.crud import get_measurement_by_id
        m_obj = get_measurement_by_id(measurement_id)
        if not m_obj:
            QMessageBox.warning(self, "Ошибка", "Измерение не найдено")
            return

        # Получаем данные
        sample_name = m_obj.sample.name if m_obj.sample else "Не указан"
        sample_id = m_obj.sample.id if m_obj.sample else None
        
        # Обработка времени
        time_str = ""
        if m_obj.time_of_event:
            if isinstance(m_obj.time_of_event, str):
                if m_obj.time_of_event.startswith("0000-00-00"):
                    time_str = ""
                else:
                    time_str = m_obj.time_of_event
            else:
                time_str = m_obj.time_of_event.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = ""

        from gui.dialogs.edit_measurement_dialog import EditMeasurementDialog
        dialog = EditMeasurementDialog({
            'id': m_obj.id,
            'sample_id': sample_id,
            'sample_name': sample_name,
            'method': m_obj.method,
            'property': m_obj.property,
            'value': float(m_obj.value),
            'unit': m_obj.unit,
            'accuracy': float(m_obj.accuracy),
            'time_of_event': time_str  # ← ДОБАВЛЕНО!
        }, self)
        if dialog.exec():
            self.reload_experiment_data()

    def delete_selected_measurement(self):
        measurement_id = self.get_selected_measurement_id()
        if not measurement_id:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить это измерение?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import delete_measurement
            if delete_measurement(measurement_id):
                QMessageBox.information(self, "Успех", "Измерение удалено")
                self.reload_experiment_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить измерение")
                
    def create_results_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        results = self.experiment_data['results']
        table = QTableWidget(len(results), 5)
        table.setHorizontalHeaderLabels(["ID", "Тип", "Описание", "Выводы", "URL"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("results_table")

        for row, r in enumerate(results):
            if r is None:
                continue
            table.setItem(row, 0, QTableWidgetItem(str(r.id)))
            table.setItem(row, 1, QTableWidgetItem(r.type))
            table.setItem(row, 2, QTableWidgetItem(r.description))
            table.setItem(row, 3, QTableWidgetItem(r.conclusions))
            table.setItem(row, 4, QTableWidgetItem(r.URL))

        layout.addWidget(table)

        # Кнопки — только для своего эксперимента
        if self.is_my_experiment():
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("➕ Добавить")
            edit_btn = QPushButton("✏️ Редактировать")
            delete_btn = QPushButton("🗑️ Удалить")

            for btn in [add_btn, edit_btn, delete_btn]:
                btn.setFixedHeight(30)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #333;
                    }
                """)

            add_btn.clicked.connect(self.add_result)
            edit_btn.clicked.connect(self.edit_selected_result)
            delete_btn.clicked.connect(self.delete_selected_result)

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            layout.addLayout(btn_layout)

        return widget
        
    def get_selected_result_id(self):
        table = self.findChild(QTableWidget, "results_table")
        if not table:
            return None
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите результат в таблице")
            return None
        row = selected[0].row()
        return int(table.item(row, 0).text())

    def add_result(self):
        from gui.dialogs.add_result_dialog import AddResultDialog
        exp_id = self.experiment_data['experiment'].id
        dialog = AddResultDialog(exp_id, self)
        if dialog.exec():
            self.reload_experiment_data()

    def edit_selected_result(self):
        result_id = self.get_selected_result_id()
        if not result_id:
            return
        from database.crud import get_result_by_id
        r_obj = get_result_by_id(result_id)
        if not r_obj:
            QMessageBox.warning(self, "Ошибка", "Результат не найден")
            return
        from gui.dialogs.edit_result_dialog import EditResultDialog
        dialog = EditResultDialog({
            'id': r_obj.id,
            'type': r_obj.type,
            'description': r_obj.description,
            'conclusions': r_obj.conclusions,
            'URL': r_obj.URL
        }, self)
        if dialog.exec():
            self.reload_experiment_data()

    def delete_selected_result(self):
        result_id = self.get_selected_result_id()
        if not result_id:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот результат?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import delete_result
            if delete_result(result_id):
                QMessageBox.information(self, "Успех", "Результат удалён")
                self.reload_experiment_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить результат")
                
    def create_conditions_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        conditions = self.experiment_data['conditions']
        table = QTableWidget(len(conditions), 7)
        table.setHorizontalHeaderLabels(["ID", "Темп. (°C)", "Давл. (Па)", "Влажн. (%)", "pH", "Освещённость", "Длительность"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("conditions_table")

        for row, c in enumerate(conditions):
            if c is None:
                continue
            # Обработка времени
            duration_str = "—"
            if c.duration:
                if isinstance(c.duration, str):
                    if c.duration.startswith("0000-00-00"):
                        duration_str = "—"
                    else:
                        try:
                            from datetime import datetime
                            dt = datetime.strptime(c.duration, '%Y-%m-%d %H:%M:%S')
                            duration_str = dt.strftime('%d.%m.%Y %H:%M')
                        except ValueError:
                            duration_str = "—"
                else:
                    duration_str = c.duration.strftime('%d.%m.%Y %H:%M')

            table.setItem(row, 0, QTableWidgetItem(str(c.id)))
            table.setItem(row, 1, QTableWidgetItem(str(c.temperature) if c.temperature is not None else "—"))
            table.setItem(row, 2, QTableWidgetItem(str(c.pressure) if c.pressure is not None else "—"))
            table.setItem(row, 3, QTableWidgetItem(str(c.humidity) if c.humidity is not None else "—"))
            table.setItem(row, 4, QTableWidgetItem(str(c.pH) if c.pH is not None else "—"))
            table.setItem(row, 5, QTableWidgetItem(c.illumination))
            table.setItem(row, 6, QTableWidgetItem(duration_str))

        layout.addWidget(table)

        # Кнопки — только для своего эксперимента
        if self.is_my_experiment():
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("➕ Добавить")
            edit_btn = QPushButton("✏️ Редактировать")
            delete_btn = QPushButton("🗑️ Удалить")

            for btn in [add_btn, edit_btn, delete_btn]:
                btn.setFixedHeight(30)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #333;
                    }
                """)

            add_btn.clicked.connect(self.add_condition)
            edit_btn.clicked.connect(self.edit_selected_condition)
            delete_btn.clicked.connect(self.delete_selected_condition)

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            layout.addLayout(btn_layout)

        return widget
        
    def get_selected_condition_id(self):
        table = self.findChild(QTableWidget, "conditions_table")
        if not table:
            return None
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите условие в таблице")
            return None
        row = selected[0].row()
        return int(table.item(row, 0).text())

    def add_condition(self):
        from gui.dialogs.add_condition_dialog import AddConditionDialog
        exp_id = self.experiment_data['experiment'].id
        dialog = AddConditionDialog(exp_id, self)
        if dialog.exec():
            self.reload_experiment_data()

    def edit_selected_condition(self):
        condition_id = self.get_selected_condition_id()
        if not condition_id:
            return
        from database.crud import get_condition_by_id
        c_obj = get_condition_by_id(condition_id)
        if not c_obj:
            QMessageBox.warning(self, "Ошибка", "Условие не найдено")
            return
        from gui.dialogs.edit_condition_dialog import EditConditionDialog
        dialog = EditConditionDialog({
            'id': c_obj.id,
            'temperature': float(c_obj.temperature) if c_obj.temperature is not None else 0.0,
            'pressure': float(c_obj.pressure) if c_obj.pressure is not None else 0.0,
            'humidity': float(c_obj.humidity) if c_obj.humidity is not None else 0.0,
            'pH': float(c_obj.pH) if c_obj.pH is not None else 0.0,
            'illumination': c_obj.illumination,
            'duration': c_obj.duration.strftime('%Y-%m-%d %H:%M:%S') if c_obj.duration and not isinstance(c_obj.duration, str) else str(c_obj.duration) if c_obj.duration else ""
        }, self)
        if dialog.exec():
            self.reload_experiment_data()

    def delete_selected_condition(self):
        condition_id = self.get_selected_condition_id()
        if not condition_id:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить это условие?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database.crud import delete_condition
            if delete_condition(condition_id):
                QMessageBox.information(self, "Успех", "Условие удалено")
                self.reload_experiment_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить условие")

    def create_table_tab(self, items, headers, item_type):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        if not items:
            label = QLabel("Нет данных")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            return widget

        table = QTableWidget(len(items), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, item in enumerate(items):
            if item_type == "method":
                table.setItem(row, 0, QTableWidgetItem(item.name))
                table.setItem(row, 1, QTableWidgetItem(item.description))
            elif item_type == "sample":
                table.setItem(row, 0, QTableWidgetItem(item.name))
                table.setItem(row, 1, QTableWidgetItem(item.chemical_formula))
                table.setItem(row, 2, QTableWidgetItem(item.aggregate_state))
                table.setItem(row, 3, QTableWidgetItem(str(item.mass)))
            elif item_type == "equipment":
                table.setItem(row, 0, QTableWidgetItem(item.name))
                table.setItem(row, 1, QTableWidgetItem(item.description))
            elif item_type == "measurement":
                sample_name = item.sample.name if item.sample else ""
                table.setItem(row, 0, QTableWidgetItem(sample_name))
                table.setItem(row, 1, QTableWidgetItem(item.method))
                table.setItem(row, 2, QTableWidgetItem(str(item.value)))
                table.setItem(row, 3, QTableWidgetItem(item.unit))
            elif item_type == "condition":
                temp = str(item.temperature) if item.temperature is not None else ""
                press = str(item.pressure) if item.pressure is not None else ""
                hum = str(item.humidity) if item.humidity is not None else ""
                ph = str(item.pH) if item.pH is not None else ""
                table.setItem(row, 0, QTableWidgetItem(temp))
                table.setItem(row, 1, QTableWidgetItem(press))
                table.setItem(row, 2, QTableWidgetItem(hum))
                table.setItem(row, 3, QTableWidgetItem(ph))
            elif item_type == "result":
                table.setItem(row, 0, QTableWidgetItem(item.type))
                table.setItem(row, 1, QTableWidgetItem(item.description))
                table.setItem(row, 2, QTableWidgetItem(item.conclusions))

        layout.addWidget(table)
        return widget
