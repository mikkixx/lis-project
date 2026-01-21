# lis_project/gui/dialogs/edit_equipment_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_equipment

class EditEquipmentDialog(BaseEditDialog):
    def __init__(self, equipment_data, parent=None):
        self.equipment_id = equipment_data['id']
        data = {
            "Название *": equipment_data['name'],
            "Описание": equipment_data['description']
        }
        fields = {
            "Название *": {"type": "text"},
            "Описание": {"type": "textarea"}
        }
        # ВАЖНО: передаём СТРОКУ как title, а не equipment_data!
        super().__init__(
            title="Редактирование оборудования",
            fields=fields,
            data=data,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        name = data.get("Название *", "").strip()
        if not name:
            self.show_error("Название обязательно")
            return
        if update_equipment(self.equipment_id, name=name, description=data["Описание"]):
            self.show_success("Оборудование обновлено!")
            super().accept()
        else:
            self.show_error("Не удалось обновить оборудование")
