# lis_project/gui/dialogs/add_measurement_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import get_samples_for_experiment, create_measurement_for_experiment
from PySide6.QtWidgets import QComboBox, QLabel

class AddMeasurementDialog(BaseEditDialog):
    def __init__(self, experiment_id, parent=None):
        self.experiment_id = experiment_id
        samples = get_samples_for_experiment(experiment_id)
        if not samples:
            raise ValueError("Нет образцов в эксперименте")

        # Подготавливаем список для комбобокса
        self.sample_options = {f"{s.name} (ID: {s.id})": s.id for s in samples}

        fields = {
            "Образец *": {"type": "combo", "options": list(self.sample_options.keys())},
            "Метод *": {"type": "text"},
            "Параметр *": {"type": "text"},
            "Значение *": {"type": "text"},
            "Единица изм. *": {"type": "text"},
            "Точность *": {"type": "text"},
            "Время измерения *": {"type": "datetime"}
        }
        super().__init__(
            title="Добавить измерение",
            fields=fields,
            data=None,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        required = ["Образец *", "Метод *", "Параметр *", "Значение *", "Единица изм. *", "Точность *", "Время измерения *"]
        for field in required:
            if not data.get(field, "").strip():
                self.show_error(f"Поле '{field}' обязательно")
                return

        sample_name = data["Образец *"]
        sample_id = self.sample_options[sample_name]
        try:
            value = float(data["Значение *"])
            accuracy = float(data["Точность *"])
        except ValueError:
            self.show_error("Значение и точность должны быть числами")
            return

        success = create_measurement_for_experiment(
            experiment_id=self.experiment_id,
            sample_id=sample_id,
            method=data["Метод *"],
            property=data["Параметр *"],
            value=value,
            unit=data["Единица изм. *"],
            accuracy=accuracy,
            time_of_event=data["Время измерения *"]
        )
        if success:
            self.show_success("Измерение добавлено!")
            super().accept()
        else:
            self.show_error("Не удалось добавить измерение")
