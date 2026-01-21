# lis_project/gui/dialogs/edit_experiment_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_experiment

class EditExperimentDialog(BaseEditDialog):
    def __init__(self, experiment_data, parent=None):
        # Сохраняем ID
        self.experiment_id = experiment_data['id']
        
        # Подготавливаем данные для формы
        data = {
            "Название *": experiment_data['name'],
            "Цель": experiment_data.get('purpose', ''),
            "Описание": experiment_data.get('description', ''),
            "План": experiment_data.get('plan', ''),
            "Дата проведения": experiment_data.get('date_of_event', ''),
            "Статус": self._status_to_rus(experiment_data['status'])
        }
        
        fields = {
            "Название *": {"type": "text"},
            "Цель": {"type": "textarea"},
            "Описание": {"type": "textarea"},
            "План": {"type": "textarea"},
            "Дата проведения": {"type": "date"},
            "Статус": {
                "type": "combo",
                "options": ["Планирование", "В работе", "Завершен"]
            }
        }
        
        # ВАЖНО: передаём СТРОКУ как title, а не experiment_data!
        super().__init__(
            title="Редактирование эксперимента",
            fields=fields,
            data=data,
            parent=parent
        )

    def _status_to_rus(self, status):
        return {'planned': 'Планирование', 'in_progress': 'В работе', 'completed': 'Завершен'}.get(status, status)

    def _status_to_en(self, status_rus):
        return {'Планирование': 'planned', 'В работе': 'in_progress', 'Завершен': 'completed'}.get(status_rus, 'planned')

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
        update_data = {
            "name": data["Название *"],
            "purpose": data["Цель"],
            "description": data.get("Описание", ""),      # ← добавлено
            "plan": data.get("План", ""),                # ← добавлено
            "status": status_map[data["Статус"]],
            "date_of_event": data["Дата проведения"]
        }
        if update_experiment(self.experiment_id, **update_data):
            self.show_success("Изменения сохранены!")
            super().accept()
        else:
            self.show_error("Не удалось обновить")
