# lis_project/gui/dialogs/create_sample_dialog.py
from .base_edit_dialog import BaseEditDialog
from database.crud import create_sample_with_researcher, get_current_researcher_id

class CreateSampleDialog(BaseEditDialog):
    def __init__(self, parent=None):
        self.researcher_id = get_current_researcher_id()
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
        # ВАЖНО: передаём ВСЕ аргументы явно
        super().__init__(
            title="Новый образец",
            fields=fields,
            data=None,
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
        sample_data = {
            "name": data["Название *"],
            "description": data["Описание"],
            "chemical_formula": data["Химическая формула"],
            "aggregate_state": data["Агрегатное состояние"],
            "mass": mass,
            "volume": volume
        }
        if create_sample_with_researcher(**sample_data, researcher_id=self.researcher_id):
            self.show_success("Образец создан!")
            super().accept()
        else:
            self.show_error("Ошибка при создании")
