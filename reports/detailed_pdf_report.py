# lis_project/reports/detailed_pdf_report.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class DetailedPDFReport:
    def __init__(self):
        self.reports_dir = "./reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        self._register_fonts()

    def _register_fonts(self):
        """Регистрация шрифтов с поддержкой кириллицы"""
        try:
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',          # Ubuntu/Debian
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
                'C:/Windows/Fonts/arial.ttf',                               # Windows
                'C:/Windows/Fonts/times.ttf'
            ]
            for path in font_paths:
                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont('CustomFont', path))
                    self.font_name = 'CustomFont'
                    return
            # Fallback
            self.font_name = 'Helvetica'
            print("⚠️ Системные шрифты не найдены. Кириллица может отображаться некорректно.")
        except Exception as e:
            print(f"Ошибка регистрации шрифтов: {e}")
            self.font_name = 'Helvetica'

    def generate(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.reports_dir, f'детальный_отчет_{timestamp}.pdf')
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=72,
            bottomMargin=36
        )
        styles = self._create_styles()
        story = []

        # === ТИТУЛЬНЫЙ ЛИСТ ===
        story.append(Paragraph("ЛАБОРАТОРНАЯ ИНФОРМАЦИОННАЯ СИСТЕМА", styles['title']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("Детальный табличный отчет", styles['heading']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['normal']))
        story.append(PageBreak())

        # === ОГЛАВЛЕНИЕ ===
        story.append(Paragraph("ОГЛАВЛЕНИЕ", styles['heading']))
        toc_items = [
            "1. Исследователи",
            "2. Эксперименты",
            "3. Образцы",
            "4. Оборудование",
            "5. Измерения",
            "6. Методы",
            "7. Результаты",
            "8. Условия экспериментов"
        ]
        for item in toc_items:
            story.append(Paragraph(item, styles['normal']))
            story.append(Spacer(1, 5))
        story.append(PageBreak())

        # === ЗАГРУЗКА ДАННЫХ ===
        from database.crud import (
            get_all_researchers,
            get_all_experiments_with_researchers,
            get_all_samples,
            get_all_equipment,
            get_all_measurements,
            get_all_methods,
            get_all_results,
            get_all_conditions
        )

        researchers = self._to_dict_list(get_all_researchers(), 'researcher')
        experiments = get_all_experiments_with_researchers() or []
        samples = self._to_dict_list(get_all_samples(), 'sample')
        equipment = self._to_dict_list(get_all_equipment(), 'equipment')
        measurements = get_all_measurements() or []
        methods = get_all_methods() or []
        results = get_all_results() or []
        conditions = get_all_conditions() or []

        # === ГЕНЕРАЦИЯ ТАБЛИЦ ===
        sections = [
            ("1. Исследователи", researchers, self._get_researchers_table),
            ("2. Эксперименты", experiments, self._get_experiments_table),
            ("3. Образцы", samples, self._get_samples_table),
            ("4. Оборудование", equipment, self._get_equipment_table),
            ("5. Измерения", measurements, self._get_measurements_table),
            ("6. Методы", methods, self._get_methods_table),
            ("7. Результаты", results, self._get_results_table),
            ("8. Условия экспериментов", conditions, self._get_conditions_table)
        ]

        for title, data, table_func in sections:
            story.append(Paragraph(title, styles['heading']))
            if data:
                table = table_func(data, styles)
                story.append(table)
            else:
                story.append(Paragraph("Нет данных", styles['normal']))
            story.append(PageBreak())

        doc.build(story)
        return f"Детальный PDF-отчёт создан: {filepath}"

    def _create_styles(self):
        styles = getSampleStyleSheet()
        return {
            'normal': ParagraphStyle(
                'NormalRU',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                leading=12,
                wordWrap='LTR'  # Включает перенос слов
            ),
            'title': ParagraphStyle(
                'TitleRU',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=18,
                alignment=1,
                spaceAfter=30
            ),
            'heading': ParagraphStyle(
                'HeadingRU',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10
            ),
            'cell': ParagraphStyle(
                'CellRU',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=8,
                leading=10,
                wordWrap='LTR',
                alignment=0  # По левому краю для лучшего переноса
            )
        }

    def _to_dict_list(self, objects, obj_type):
        """Преобразует объекты Peewee в словари"""
        if not objects:
            return []
        result = []
        for obj in objects:
            if hasattr(obj, '__data__'):
                result.append(obj.__data__)
            elif hasattr(obj, '_data'):
                result.append(obj._data)
            else:
                d = {}
                for field in dir(obj):
                    if not field.startswith('_') and not callable(getattr(obj, field)):
                        d[field] = getattr(obj, field)
                result.append(d)
        return result

    def _get_researchers_table(self, data, styles):
        headers = ["ID", "Фамилия", "Имя", "Отчество", "Организация", "Email"]
        rows = []
        for r in data:
            rows.append([
                str(r.get('id', '')),
                r.get('surname', ''),
                r.get('name', ''),
                r.get('patronymic', ''),
                r.get('organization', ''),
                r.get('email', '')
            ])
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.0*inch, 0.9*inch, 1.0*inch, 1.8*inch, 1.5*inch])

    def _get_experiments_table(self, data, styles):
        status_map = {'planned': 'Планирование', 'in_progress': 'В работе', 'completed': 'Завершен'}
        headers = ["ID", "Название", "Цель", "Статус", "Дата", "Исследователь"]
        rows = []
        for e in data:
            rows.append([
                str(e['id']),
                e['name'],
                e['purpose'],
                status_map.get(e['status'], e['status']),
                e['date'],
                e['researcher']
            ])
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.2*inch, 1.2*inch, 0.9*inch, 0.8*inch, 1.5*inch])

    def _get_samples_table(self, data, styles):
        headers = ["ID", "Название", "Формула", "Состояние", "Масса (г)", "Объём (мл)"]
        rows = []
        for s in data:
            rows.append([
                str(s.get('id', '')),
                s.get('name', ''),
                s.get('chemical_formula', ''),
                s.get('aggregate_state', ''),
                str(s.get('mass', '')) if s.get('mass') is not None else '',
                str(s.get('volume', '')) if s.get('volume') is not None else ''
            ])
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.2*inch, 1.0*inch, 1.0*inch, 0.8*inch, 0.8*inch])

    def _get_equipment_table(self, data, styles):
        headers = ["ID", "Название", "Описание"]
        rows = [[str(e.get('id', '')), e.get('name', ''), e.get('description', '')] for e in data]
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.5*inch, 4.5*inch])

    def _get_measurements_table(self, data, styles):
        headers = ["ID", "Метод", "Параметр", "Значение", "Ед.", "Образец"]
        rows = []
        for m in data:
            rows.append([
                str(m['id']),
                m['method'],
                m['property'],
                str(m['value']),
                m['unit'],
                m['sample_name']
            ])
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.0*inch, 1.0*inch, 0.8*inch, 0.6*inch, 2.0*inch])

    def _get_methods_table(self, data, styles):
        headers = ["ID", "Название", "Описание", "Эксперимент"]
        rows = [[str(m['id']), m['name'], m['description'], m['experiment_name']] for m in data]
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.2*inch, 2.5*inch, 2.0*inch])

    def _get_results_table(self, data, styles):
        headers = ["ID", "Тип", "Описание", "Выводы", "Эксперимент"]
        rows = [[str(r['id']), r['type'], r['description'], r['conclusions'], r['experiment_name']] for r in data]
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 1.0*inch, 1.8*inch, 1.8*inch, 1.5*inch])

    def _get_conditions_table(self, data, styles):
        headers = ["ID", "Темп. (°C)", "Давл. (Па)", "Влажн. (%)", "pH", "Освещение", "Эксперимент"]
        rows = []
        for c in data:
            rows.append([
                str(c['id']),
                str(c.get('temperature', '')) if c.get('temperature') is not None else '-',
                str(c.get('pressure', '')) if c.get('pressure') is not None else '-',
                str(c.get('humidity', '')) if c.get('humidity') is not None else '-',
                str(c.get('pH', '')) if c.get('pH') is not None else '-',
                c.get('illumination', ''),
                c['experiment_name']
            ])
        return self._create_table(headers, rows, styles['cell'], [0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.5*inch, 1.2*inch, 1.8*inch])

    def _create_table(self, headers, rows, cell_style, col_widths):
        """Создаёт таблицу с переносом текста"""
        table_data = [headers]
        for row in rows:
            wrapped_row = [Paragraph(str(cell), cell_style) for cell in row]
            table_data.append(wrapped_row)

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table
