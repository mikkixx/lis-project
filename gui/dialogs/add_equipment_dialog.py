# lis_project/gui/dialogs/add_equipment_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import create_equipment_and_link_to_experiment

class AddEquipmentDialog(BaseEditDialog):
    def __init__(self, experiment_id, parent=None):
        self.experiment_id = experiment_id
        fields = {
            "Название *": {"type": "text"},
            "Описание": {"type": "textarea"}
        }
        # ВАЖНО: передаём СТРОКУ как title, а не experiment_id!
        super().__init__(
            title="Добавить оборудование",
            fields=fields,
            data=None,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        name = data.get("Название *", "").strip()
        if not name:
            self.show_error("Название обязательно")
            return
        description = data.get("Описание", "")
        success = create_equipment_and_link_to_experiment(
            self.experiment_id, name, description
        )
        if success:
            self.show_success("Оборудование добавлено!")
            super().accept()
        else:
            self.show_error("Не удалось добавить оборудование")
