# lis_project/gui/dialogs/edit_sample_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import update_sample

class EditSampleDialog(BaseEditDialog):
    def __init__(self, sample_data, parent=None):
        self.sample_id = sample_data['id']
        data = {
            "Название *": sample_data['name'],
            "Описание": sample_data['description'],
            "Химическая формула": sample_data['chemical_formula'],
            "Агрегатное состояние": sample_data['aggregate_state'],
            "Масса (г)": str(sample_data['mass']),
            "Объем (см³)": str(sample_data['volume'])
        }
        fields = {
            "Название *": {"type": "text"},
            "Описание": {"type": "textarea"},
            "Химическая формула": {"type": "text"},
            "Агрегатное состояние": {"type": "combo", "options": [
                "Твердое (кристаллическое)", "Твердое (металл)", "Твердое (порошок)",
                "Жидкое", "Газообразное"
            ]},
            "Масса (г)": {"type": "text"},
            "Объем (см³)": {"type": "text"}
        }
        # ВАЖНО: передаём СТРОКУ как title, а не sample_data!
        super().__init__(
            title="Редактирование образца",
            fields=fields,
            data=data,
            parent=parent
        )

    def accept(self):
        data = self.get_data()
        if not data.get("Название *").strip():
            self.show_error("Название обязательно")
            return
        try:
            mass = float(data["Масса (г)"]) if data["Масса (г)"] else 0.0
            volume = float(data["Объем (см³)"]) if data["Объем (см³)"] else 0.0
        except ValueError:
            self.show_error("Масса и объем должны быть числами")
            return
        update_data = {
            "name": data["Название *"],
            "description": data["Описание"],
            "chemical_formula": data["Химическая формула"],
            "aggregate_state": data["Агрегатное состояние"],
            "mass": mass,
            "volume": volume
        }
        if update_sample(self.sample_id, **update_data):
            self.show_success("Изменения сохранены!")
            super().accept()
        else:
            self.show_error("Не удалось обновить")
