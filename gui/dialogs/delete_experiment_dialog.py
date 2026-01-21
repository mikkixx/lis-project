from .base_edit_dialog import BaseEditDialog
from database.crud import delete_experiment

class DeleteExperimentDialog(BaseEditDialog):
    def init(self, experiment_id, experiment_name, parent=None):
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        # Создаём минимальный "фейковый" fields, чтобы BaseEditDialog не ругался
        fields = {"Подтверждение": {"type": "text"}}
        data = {"Подтверждение": f"Вы уверены, что хотите удалить эксперимент «{experiment_name}»?\nЭто действие нельзя отменить. Будут удалены все связанные методы, результаты, условия и связи."}
        super().init("Удаление эксперимента", fields, data=data, parent=parent)
        # Скрываем поле ввода и кнопку "Сохранить"
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
        if delete_experiment(self.experiment_id):
            self.show_success(f"Эксперимент «{self.experiment_name}» успешно удалён!")
            super().accept()
        else:
            self.show_error("Не удалось удалить эксперимент.")
