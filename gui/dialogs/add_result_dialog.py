# lis_project/gui/dialogs/add_result_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import create_result_for_experiment

class AddResultDialog(BaseEditDialog):
    def __init__(self, experiment_id, parent=None):
        self.experiment_id = experiment_id
        fields = {
            "Тип *": {"type": "text"},
            "Описание *": {"type": "textarea"},
            "Выводы *": {"type": "textarea"},
            "URL": {"type": "text"}
        }
        super().__init__(
            title="Добавить результат",
            fields=fields,
            data=None,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        required = ["Тип *", "Описание *", "Выводы *"]
        for field in required:
            if not data.get(field, "").strip():
                self.show_error(f"Поле '{field}' обязательно")
                return
        success = create_result_for_experiment(
            self.experiment_id,
            type=data["Тип *"],
            description=data["Описание *"],
            conclusions=data["Выводы *"],
            URL=data.get("URL", "")
        )
        if success:
            self.show_success("Результат добавлен!")
            super().accept()
        else:
            self.show_error("Не удалось добавить результат")
