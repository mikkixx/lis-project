from .base_edit_dialog import BaseEditDialog

class ResearcherProfileDialog(BaseEditDialog):
    def init(self, researcher_data, parent=None):
        data = {
            "Фамилия": researcher_data.get("surname", ""),
            "Имя": researcher_data.get("name", ""),
            "Отчество": researcher_data.get("patronymic", ""),
            "Биография": researcher_data.get("biography", ""),
            "Ученая степень": researcher_data.get("academic_degree", ""),
            "Организация": researcher_data.get("organization", ""),
            "Email": researcher_data.get("email", ""),
            "URL соц сети": researcher_data.get("URL", "")
        }
        fields = {
            "Фамилия": {"type": "text"},
            "Имя": {"type": "text"},
            "Отчество": {"type": "text"},
            "Биография": {"type": "textarea"},
            "Ученая степень": {"type": "text"},
            "Организация": {"type": "text"},
            "Email": {"type": "text"},
            "URL соц сети": {"type": "text"}
        }
        super().init("Профиль исследователя", fields, data=data, parent=parent)
        # Только просмотр — скрываем кнопку сохранения
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Сохранить":
                btn.setVisible(False)
                break
