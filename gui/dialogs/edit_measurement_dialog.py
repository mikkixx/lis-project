# lis_project/gui/dialogs/edit_measurement_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_measurement

class EditMeasurementDialog(BaseEditDialog):
    # В edit_measurement_dialog.py
    def __init__(self, measurement_data, parent=None):
        self.measurement_id = measurement_data['id']
        data = {
            "Образец *": f"{measurement_data['sample_name']} (ID: {measurement_data['sample_id']})",
            "Метод *": measurement_data['method'],
            "Параметр *": measurement_data['property'],
            "Значение *": str(measurement_data['value']),
            "Единица изм. *": measurement_data['unit'],
            "Точность *": str(measurement_data['accuracy']),
            "Время измерения *": measurement_data['time_of_event']  # должно быть строкой в формате 'YYYY-MM-DD HH:MM:SS'
        }
        fields = {
            "Образец *": {"type": "text"},  # делаем readonly — нельзя менять образец
            "Метод *": {"type": "text"},
            "Параметр *": {"type": "text"},
            "Значение *": {"type": "text"},
            "Единица изм. *": {"type": "text"},
            "Точность *": {"type": "text"},
            "Время измерения *": {"type": "datetime"}
        }
        super().__init__(
            title="Редактирование измерения",
            fields=fields,
            data=data,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        required = ["Метод *", "Параметр *", "Значение *", "Единица изм. *", "Точность *"]
        for field in required:
            if not data.get(field, "").strip():
                self.show_error(f"Поле '{field}' обязательно")
                return
        try:
            value = float(data["Значение *"])
            accuracy = float(data["Точность *"])
        except ValueError:
            self.show_error("Значение и точность должны быть числами")
            return
        update_data = {
            "method": data["Метод *"],
            "property": data["Параметр *"],
            "value": value,
            "unit": data["Единица изм. *"],
            "accuracy": accuracy
        }
        if update_measurement(self.measurement_id, **update_data):
            self.show_success("Измерение обновлено!")
            super().accept()
        else:
            self.show_error("Не удалось обновить измерение")
