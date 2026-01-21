# lis_project/gui/dialogs/edit_result_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_result

class EditResultDialog(BaseEditDialog):
    def __init__(self, result_data, parent=None):
        self.result_id = result_data['id']
        data = {
            "Тип *": result_data['type'],
            "Описание *": result_data['description'],
            "Выводы *": result_data['conclusions'],
            "URL": result_data['URL']
        }
        fields = {
            "Тип *": {"type": "text"},
            "Описание *": {"type": "textarea"},
            "Выводы *": {"type": "textarea"},
            "URL": {"type": "text"}
        }
        super().__init__(
            title="Редактирование результата",
            fields=fields,
            data=data,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        required = ["Тип *", "Описание *", "Выводы *"]
        for field in required:
            if not data.get(field, "").strip():
                self.show_error(f"Поле '{field}' обязательно")
                return
        update_data = {
            "type": data["Тип *"],
            "description": data["Описание *"],
            "conclusions": data["Выводы *"],
            "URL": data.get("URL", "")
        }
        if update_result(self.result_id, **update_data):
            self.show_success("Результат обновлён!")
            super().accept()
        else:
            self.show_error("Не удалось обновить результат")
