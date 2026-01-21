from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel
)
from PySide6.QtGui import QFont
from gui.pages import (
    MainPage, ExperimentsPage, ResearchersPage, SamplesPage,
    MyExperimentsPage, MySamplesPage
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная информационная система | ЛИС")
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === БОКОВОЕ МЕНЮ ===
        self.menu_widget = QWidget()
        self.menu_widget.setFixedWidth(220)
        self.menu_widget.setStyleSheet("background-color: #f5f5f5; border-right: 1px solid #ccc;")
        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setSpacing(10)
        menu_layout.setContentsMargins(10, 20, 10, 20)

        title = QLabel("ЛИС")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #000; margin-bottom: 20px;")
        menu_layout.addWidget(title)

        # Кнопки меню
        self.btn_main = self._create_menu_button("Главная", self.show_main)
        self.btn_experiments = self._create_menu_button("Все эксперименты", self.show_experiments)
        self.btn_samples = self._create_menu_button("Все образцы", self.show_samples)
        self.btn_researchers = self._create_menu_button("Исследователи", self.show_researchers)
        self.btn_my_exp = self._create_menu_button("Мои эксперименты", self.show_my_experiments)
        self.btn_my_samples = self._create_menu_button("Мои образцы", self.show_my_samples)
        self.btn_reports = self._create_menu_button("Отчёты", self.show_reports)

        menu_layout.addWidget(self.btn_main)
        menu_layout.addWidget(self.btn_experiments)
        menu_layout.addWidget(self.btn_samples)
        menu_layout.addWidget(self.btn_researchers)
        menu_layout.addWidget(self.btn_my_exp)
        menu_layout.addWidget(self.btn_my_samples)
        menu_layout.addWidget(self.btn_reports)
        menu_layout.addStretch()

        # === СТЕК СТРАНИЦ ===
        self.stacked_widget = QStackedWidget()

        # Создаём страницы
        self.main_page = MainPage(self)
        self.experiments_page = ExperimentsPage(self)
        self.samples_page = SamplesPage(self)
        self.researchers_page = ResearchersPage(self)
        self.my_experiments_page = MyExperimentsPage(self)
        self.my_samples_page = MySamplesPage(self)

        for page in [self.main_page, self.experiments_page, self.samples_page,
                     self.researchers_page, self.my_experiments_page, self.my_samples_page]:
            self.stacked_widget.addWidget(page)

        # Собираем всё вместе
        main_layout.addWidget(self.menu_widget)
        main_layout.addWidget(self.stacked_widget)

    def _create_menu_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                background-color: #fff;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def show_main(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_experiments(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_samples(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_researchers(self):
        self.stacked_widget.setCurrentIndex(3)

    def show_my_experiments(self):
        self.stacked_widget.setCurrentIndex(4)

    def show_my_samples(self):
        self.stacked_widget.setCurrentIndex(5)

    def show_reports(self):
        from gui.dialogs.reports_dialog import ReportsDialog
        dialog = ReportsDialog(self)
        dialog.exec()
