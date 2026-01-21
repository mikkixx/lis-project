# lis_project/gui/dialogs/create_experiment_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import create_experiment, get_current_researcher_id

class CreateExperimentDialog(BaseEditDialog):
    def __init__(self, parent=None):
        self.researcher_id = get_current_researcher_id()
        fields = {
            "Название *": {"type": "text"},
            "Цель": {"type": "textarea"},
            "Статус": {"type": "combo", "options": ["Планирование", "В работе", "Завершен"]},
            "Дата проведения": {"type": "date"}
        }
        super().__init__("Новый эксперимент", fields, data=None, parent=parent)

    def accept(self):
        data = self.get_data()
        if not data.get("Название *").strip():
            self.show_error("Название обязательно")
            return
        status_map = {
            "Планирование": "planned",
            "В работе": "in_progress",
            "Завершен": "completed"
        }
        exp_data = {
            "name": data["Название *"],
            "purpose": data["Цель"],
            "status": status_map[data["Статус"]],
            "date_of_event": data["Дата проведения"]
        }
        if create_experiment(**exp_data, researcher_id=self.researcher_id):
            self.show_success("Эксперимент создан!")
            super().accept()
        else:
            self.show_error("Ошибка при создании")
