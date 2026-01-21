# lis_project/gui/dialogs/add_condition_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import create_condition_for_experiment

class AddConditionDialog(BaseEditDialog):
    def __init__(self, experiment_id, parent=None):
        self.experiment_id = experiment_id
        fields = {
            "Температура (°C) *": {"type": "text"},
            "Давление (Па) *": {"type": "text"},
            "Влажность (%) *": {"type": "text"},
            "pH *": {"type": "text"},
            "Освещённость *": {"type": "text"},
            "Длительность *": {"type": "datetime"}
        }
        super().__init__(
            title="Добавить условие",
            fields=fields,
            data=None,
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
        success = create_condition_for_experiment(
            self.experiment_id,
            temperature=temperature,
            pressure=pressure,
            humidity=humidity,
            pH=pH,
            illumination=data["Освещённость *"],
            duration=data["Длительность *"]
        )
        if success:
            self.show_success("Условие добавлено!")
            super().accept()
        else:
            self.show_error("Не удалось добавить условие")
