# lis_project/gui/dialogs/reports_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import traceback

class ReportsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генерация отчётов")
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Выберите тип отчёта")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Кнопки отчётов
        excel_btn = QPushButton("📊 Excel-отчёт")
        stat_pdf_btn = QPushButton("📈 Статистический PDF")
        detail_pdf_btn = QPushButton("📋 Детальный PDF")

        for btn in [excel_btn, stat_pdf_btn, detail_pdf_btn]:
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #000;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """)

        excel_btn.clicked.connect(self.generate_excel)
        stat_pdf_btn.clicked.connect(self.generate_stat_pdf)
        detail_pdf_btn.clicked.connect(self.generate_detail_pdf)

        layout.addWidget(excel_btn)
        layout.addWidget(stat_pdf_btn)
        layout.addWidget(detail_pdf_btn)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setFixedHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #000;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
        """)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def generate_excel(self):
        try:
            from reports.excel_report import ExcelReportGenerator
            generator = ExcelReportGenerator()
            msg = generator.generate()
            QMessageBox.information(self, "Успех", msg)
        except Exception as e:
            print("Ошибка Excel:", e)
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать Excel-отчёт:\n{str(e)}")

    def generate_stat_pdf(self):
        try:
            from reports.statistical_pdf_report import StatisticalPDFReport
            generator = StatisticalPDFReport()
            msg = generator.generate()
            QMessageBox.information(self, "Успех", msg)
        except Exception as e:
            print("Ошибка стат. PDF:", e)
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать статистический PDF:\n{str(e)}")

    def generate_detail_pdf(self):
        try:
            from reports.detailed_pdf_report import DetailedPDFReport
            generator = DetailedPDFReport()
            msg = generator.generate()
            QMessageBox.information(self, "Успех", msg)
        except Exception as e:
            print("Ошибка дет. PDF:", e)
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать детальный PDF:\n{str(e)}")
