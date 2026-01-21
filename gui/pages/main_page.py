# lis_project/gui/pages/main_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMainWindow
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from datetime import datetime, timedelta
import traceback

class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()

        # === Заголовок ===
        top_layout = QHBoxLayout()
        title = QLabel("Главная страница")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #000000; margin: 10px;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        # Кнопка "Мой профиль"
        profile_btn = QPushButton("Мой профиль")
        profile_btn.setFixedSize(120, 35)
        profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        profile_btn.clicked.connect(self.show_profile)
        top_layout.addWidget(profile_btn)

        layout.addLayout(top_layout)

        # === Разделитель ===
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(line)

        # === Прокручиваемая область ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # Статистика
        stats_label = QLabel("Статистика")
        stats_label.setFont(QFont("Arial", 16, QFont.Bold))
        stats_label.setStyleSheet("color: #000000; margin: 10px;")
        self.scroll_layout.addWidget(stats_label)

        self.stats_table = self.create_stats_table()
        self.scroll_layout.addWidget(self.stats_table)

        # Последние эксперименты
        exp_label = QLabel("Последние эксперименты")
        exp_label.setFont(QFont("Arial", 16, QFont.Bold))
        exp_label.setStyleSheet("color: #000000; margin: 10px;")
        self.scroll_layout.addWidget(exp_label)

        self.experiments_table = self.create_experiments_table()
        self.scroll_layout.addWidget(self.experiments_table)

        # График
        chart_label = QLabel("Количество экспериментов по месяцам")
        chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        chart_label.setStyleSheet("color: #000000; margin: 10px;")
        self.scroll_layout.addWidget(chart_label)

        self.chart_widget = self.create_chart()
        self.scroll_layout.addWidget(self.chart_widget)
        self.scroll_layout.addStretch()

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        self.profile_btn = profile_btn
        self.setLayout(layout)

        # Загрузка данных с небольшой задержкой (чтобы GUI успел отобразиться)
        QTimer.singleShot(100, self.load_data)

    def show_profile(self):
        from database.crud import get_researcher_by_id
        from gui.dialogs.researcher_profile_view_dialog import ResearcherProfileViewDialog

        researcher_obj = get_researcher_by_id(1)
        if researcher_obj:
            # Преобразуем объект Peewee в словарь
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
            dialog = ResearcherProfileViewDialog(researcher_data, self)
            dialog.exec()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Профиль не найден")

    def load_data(self):
        try:
            from database.crud import get_all_experiments_with_researchers, get_all_researchers
            experiments = get_all_experiments_with_researchers() or []
            researchers = get_all_researchers() or []

            total_experiments = len(experiments)
            total_researchers = len(researchers)
            recent = sum(1 for e in experiments if e.get('date') and 
                        datetime.strptime(e['date'], '%d.%m.%Y') > datetime.now() - timedelta(days=30))

            self.stats_table.setRowCount(3)
            for i, (name, val) in enumerate([
                ("Эксперименты", str(total_experiments)),
                ("Исследователи", str(total_researchers)),
                ("Новые за месяц", str(recent))
            ]):
                self.stats_table.setItem(i, 0, QTableWidgetItem(name))
                self.stats_table.setItem(i, 1, QTableWidgetItem(val))

            # Последние 5 экспериментов
            sorted_exp = sorted(
                [e for e in experiments if e['date'] != 'Не указана'],
                key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'),
                reverse=True
            )[:5]
            self.experiments_table.setRowCount(len(sorted_exp))
            for row, exp in enumerate(sorted_exp):
                self.experiments_table.setItem(row, 0, QTableWidgetItem(exp['name']))
                self.experiments_table.setItem(row, 1, QTableWidgetItem(exp['status']))
                self.experiments_table.setItem(row, 2, QTableWidgetItem(exp['date']))

            self.update_chart()

        except Exception as e:
            print("❌ Ошибка загрузки данных:", e)
            traceback.print_exc()

    def update_chart(self):
        try:
            from database.crud import get_all_experiments_with_researchers
            from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
            from PySide6.QtGui import QPainter, QColor

            experiments = get_all_experiments_with_researchers() or []
            monthly = {i: 0 for i in range(1, 13)}
            for e in experiments:
                if e['date'] != "Не указана":
                    try:
                        d = datetime.strptime(e['date'], "%d.%m.%Y")
                        monthly[d.month] += 1
                    except:
                        pass

            months = ["Янв", "Фев", "Март", "Апр", "Май", "Июнь",
                      "Июль", "Авг", "Сен", "Окт", "Нояб", "Дек"]
            values = [monthly[i] for i in range(1, 13)]

            chart = QChart()
            series = QBarSeries()
            bar_set = QBarSet("Эксперименты")
            for v in values:
                bar_set.append(v)
            bar_set.setColor(QColor("#000000"))
            series.append(bar_set)
            chart.addSeries(series)

            axis_x = QBarCategoryAxis()
            axis_x.append(months)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            axis_y = QValueAxis()
            axis_y.setRange(0, max(values) + 1 if max(values) > 0 else 1)
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)

            chart.legend().setVisible(False)
            chart.setBackgroundBrush(Qt.white)

            while self.chart_widget.layout().count():
                child = self.chart_widget.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setFixedHeight(300)
            chart_view.setStyleSheet("border: 1px solid #cccccc; border-radius: 8px;")
            self.chart_widget.layout().addWidget(chart_view)

        except Exception as e:
            print("❌ Ошибка обновления графика:", e)
            traceback.print_exc()

    def create_stats_table(self):
        from PySide6.QtWidgets import QTableWidget, QHeaderView
        table = QTableWidget(3, 2)
        table.setHorizontalHeaderLabels(["Параметр", "Количество"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setFixedHeight(150)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #000000;
            }
        """)
        return table

    def create_experiments_table(self):
        from PySide6.QtWidgets import QTableWidget, QHeaderView
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Название", "Статус", "Дата"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setFixedHeight(180)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #000000;
            }
        """)
        return table

    def create_chart(self):
        from PySide6.QtWidgets import QWidget, QHBoxLayout
        chart_container = QWidget()
        chart_layout = QHBoxLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        return chart_container
