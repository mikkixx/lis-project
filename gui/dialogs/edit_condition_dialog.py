# lis_project/gui/dialogs/edit_condition_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_condition

class EditConditionDialog(BaseEditDialog):
    def __init__(self, condition_data, parent=None):
        self.condition_id = condition_data['id']
        data = {
            "Температура (°C) *": str(condition_data['temperature']),
            "Давление (Па) *": str(condition_data['pressure']),
            "Влажность (%) *": str(condition_data['humidity']),
            "pH *": str(condition_data['pH']),
            "Освещённость *": condition_data['illumination'],
            "Длительность *": condition_data['duration']
        }
        fields = {
            "Температура (°C) *": {"type": "text"},
            "Давление (Па) *": {"type": "text"},
            "Влажность (%) *": {"type": "text"},
            "pH *": {"type": "text"},
            "Освещённость *": {"type": "text"},
            "Длительность *": {"type": "datetime"}
        }
        super().__init__(
            title="Редактирование условия",
            fields=fields,
            data=data,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        required = ["Температура (°C) *", "Давление (Па) *", "Влажность (%) *", "pH *", "Освещённость *", "Длительность *"]
        for field in required:
            if not data.get(field, "").strip():
                self.show_error(f"Поле '{field}' обязательно")
                return
        try:
            temperature = float(data["Температура (°C) *"])
            pressure = float(data["Давление (Па) *"])
            humidity = float(data["Влажность (%) *"])
            pH = float(data["pH *"])
        except ValueError:
            self.show_error("Числовые поля должны содержать числа")
            return
        update_data = {
            "temperature": temperature,
            "pressure": pressure,
            "humidity": humidity,
            "pH": pH,
            "illumination": data["Освещённость *"],
            "duration": data["Длительность *"]
        }
        if update_condition(self.condition_id, **update_data):
            self.show_success("Условие обновлено!")
            super().accept()
        else:
            self.show_error("Не удалось обновить условие")
