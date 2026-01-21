from .base_edit_dialog import BaseEditDialog
from database.crud import get_researcher_by_id, update_researcher

class ProfileDialog(BaseEditDialog):
    def __init__(self, researcher_id, parent=None):
        self.researcher_id = researcher_id
        
        # Получаем данные исследователя из БД
        researcher_obj = get_researcher_by_id(researcher_id)
        
        if researcher_obj:
            data = {
                "Фамилия": researcher_obj.surname,
                "Имя": researcher_obj.name,
                "Отчество": researcher_obj.patronymic,
                "Биография": researcher_obj.biography,
                "Ученая степень": researcher_obj.academic_degree,
                "Организация": researcher_obj.organization,
                "Email": researcher_obj.email,
                "URL соц сети": researcher_obj.URL
            }
        else:
            # Если исследователь не найден — пустые поля
            data = {
                "Фамилия": "",
                "Имя": "",
                "Отчество": "",
                "Биография": "",
                "Ученая степень": "",
                "Организация": "",
                "Email": "",
                "URL соц сети": ""
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

        super().__init__("Мой профиль", fields, data=data, parent=parent)

    def accept(self):
        data = self.get_data()
        
        # Валидация обязательных полей
        if not data.get("Фамилия").strip():
            self.show_error("Фамилия обязательна")
            return
        if not data.get("Имя").strip():
            self.show_error("Имя обязательно")
            return
        if not data.get("Организация").strip():
            self.show_error("Организация обязательна")
            return

        # Подготавливаем данные для обновления
        update_data = {
            "surname": data["Фамилия"],
            "name": data["Имя"],
            "patronymic": data["Отчество"],
            "biography": data["Биография"],
            "academic_degree": data["Ученая степень"],
            "organization": data["Организация"],
            "email": data["Email"],
            "URL": data["URL соц сети"]
        }

        # Сохраняем в БД
        if update_researcher(self.researcher_id, **update_data):
            self.show_success("Профиль успешно обновлён!")
            super().accept()
        else:
            self.show_error("Не удалось сохранить изменения. Проверьте подключение к базе данных.")
