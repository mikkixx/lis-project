# lis_project/gui/dialogs/edit_method_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_method

class EditMethodDialog(BaseEditDialog):
    def __init__(self, method_data, parent=None):
        self.method_id = method_data['id']
        data = {
            "Название метода *": method_data['name'],
            "Описание метода": method_data['description']
        }
        fields = {
            "Название метода *": {"type": "text"},
            "Описание метода": {"type": "textarea"}
        }
        # ВАЖНО: передаём СТРОКУ как title, а не method_data!
        super().__init__(
            title="Редактирование метода",
            fields=fields,
            data=data,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        name = data.get("Название метода *", "").strip()
        if not name:
            self.show_error("Название обязательно")
            return
        update_data = {
            "name": name,
            "description": data["Описание метода"]
        }
        if update_method(self.method_id, **update_data):
            self.show_success("Метод обновлён!")
            super().accept()
        else:
            self.show_error("Не удалось обновить метод")
