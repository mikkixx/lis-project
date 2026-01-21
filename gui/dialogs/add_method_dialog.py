from .base_edit_dialog import BaseEditDialog
from database.crud import create_method

class AddMethodDialog(BaseEditDialog):
    def __init__(self, experiment_id, parent=None):
        self.experiment_id = experiment_id
        fields = {
            "Название метода *": {"type": "text"},
            "Описание метода": {"type": "textarea"}
        }
        # ВАЖНО: передаём СТРОКУ как title, а не experiment_id!
        super().__init__(
            title="Добавление метода",
            fields=fields,
            data=None,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        name = data.get("Название метода *", "").strip()
        if not name:
            self.show_error("Название обязательно")
            return
        if create_method(self.experiment_id, name, data["Описание метода"]):
            self.show_success("Метод добавлен!")
            super().accept()
        else:
            self.show_error("Ошибка при добавлении")
