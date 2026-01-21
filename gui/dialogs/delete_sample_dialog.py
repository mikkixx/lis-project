from .base_edit_dialog import BaseEditDialog
from database.crud import delete_sample_completely

class DeleteSampleDialog(BaseEditDialog):
    def init(self, sample_id, sample_name, parent=None):
        self.sample_id = sample_id
        self.sample_name = sample_name
        fields = {"Подтверждение": {"type": "text"}}
        data = {"Подтверждение": f"Вы уверены, что хотите полностью удалить образец «{sample_name}»?\nБудут удалены все измерения и связи с экспериментами."}
        super().init("Удаление образца", fields, data=data, parent=parent)
        self.fields["Подтверждение"].setReadOnly(True)
        self.fields["Подтверждение"].setStyleSheet("color: #000000; background-color: #f0f0f0;")
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Сохранить":
                btn.setText("Удалить")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d32f2f;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #b71c1c; }
                    QPushButton:pressed { background-color: #9a0007; }
                """)

    def accept(self):
        if delete_sample_completely(self.sample_id):
            self.show_success(f"Образец «{self.sample_name}» успешно удалён!")
            super().accept()
        else:
            self.show_error("Не удалось удалить образец.")
