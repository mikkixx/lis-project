# lis_project/gui/dialogs/base_edit_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QPushButton, QMessageBox, QDateTimeEdit
)
from PySide6.QtCore import Qt, QDateTime

class BaseEditDialog(QDialog):
    def __init__(self, title, fields, data=None, parent=None):
        # Важно: передаём ТОЛЬКО parent в QDialog
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setFixedSize(500, 450)
        self.fields = {}

        layout = QVBoxLayout(self)

        form = QFormLayout()
        for name, spec in fields.items():
            if spec["type"] == "text":
                widget = QLineEdit(spec.get("default", ""))
                if data and name in data:
                    widget.setText(str(data[name]))
            elif spec["type"] == "textarea":
                widget = QTextEdit(spec.get("default", ""))
                widget.setFixedHeight(80)
                if data and name in data:
                    widget.setPlainText(str(data[name]))
            elif spec["type"] == "combo":
                widget = QComboBox()
                widget.addItems(spec["options"])
                if data and name in data and data[name] in spec["options"]:
                    widget.setCurrentText(data[name])
            elif spec["type"] == "date":
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd.MM.yyyy")
                if data and name in data and data[name]:
                    try:
                        qdt = QDateTime.fromString(data[name], "yyyy-MM-dd")
                        widget.setDateTime(qdt)
                    except:
                        widget.setDateTime(QDateTime.currentDateTime())
                else:
                    widget.setDateTime(QDateTime.currentDateTime())
            elif spec["type"] == "datetime":
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd.MM.yyyy HH:mm")
                if data and name in data and data[name]:
                    try:
                        qdt = QDateTime.fromString(data[name], "yyyy-MM-dd HH:mm:ss")
                        widget.setDateTime(qdt)
                    except:
                        widget.setDateTime(QDateTime.currentDateTime())
                else:
                    widget.setDateTime(QDateTime.currentDateTime())
            else:
                continue
            self.fields[name] = widget
            form.addRow(name, widget)

        layout.addLayout(form)

        # Кнопки
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отменить")
        for btn in (save_btn, cancel_btn):
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #000; color: white; border: none;
                    border-radius: 8px; font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background-color: #333; }
                QPushButton:pressed { background-color: #666; }
            """)
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        result = {}
        for name, widget in self.fields.items():
            if isinstance(widget, QTextEdit):
                result[name] = widget.toPlainText().strip()
            elif isinstance(widget, QDateTimeEdit):
                dt = widget.dateTime().toPython()
                if "time" in name.lower():
                    result[name] = dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    result[name] = dt.strftime("%Y-%m-%d")
            else:
                result[name] = widget.text().strip() if hasattr(widget, 'text') else widget.currentText()
        return result

    def show_error(self, msg):
        QMessageBox.warning(self, "Ошибка", msg)

    def show_success(self, msg):
        QMessageBox.information(self, "Успех", msg)
