# lis_project/reports/excel_report.py
import os
import xlsxwriter
from datetime import datetime
from database.crud import (
    get_all_experiments_with_researchers,
    get_all_samples,
    get_all_measurements
)

class ExcelReportGenerator:
    def __init__(self):
        self.reports_dir = "./reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.reports_dir, f'лабораторный_отчет_{timestamp}.xlsx')
        try:
            workbook = xlsxwriter.Workbook(filepath)
            header_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'bg_color': '#366092',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter'
            })
            table_header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1,
                'align': 'center'
            })
            number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
            text_format = workbook.add_format({'border': 1})

            self.create_data_sheet(workbook, header_format, title_format, table_header_format, number_format, text_format)
            self.create_analytics_sheet(workbook, header_format, title_format, table_header_format, number_format, text_format)
            self.create_visualization_sheet(workbook, header_format, title_format)

            workbook.close()
            return f"Excel отчет успешно создан: {filepath}"
        except Exception as e:
            raise Exception(f"Ошибка при создании Excel отчета: {str(e)}")

    def create_data_sheet(self, workbook, header_format, title_format, table_header_format, number_format, text_format):
        worksheet = workbook.add_worksheet('Данные проекта')
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 35)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 15)

        worksheet.merge_range('A1:G1', 'ЛАБОРАТОРНАЯ ИНФОРМАЦИОННАЯ СИСТЕМА', title_format)
        worksheet.merge_range('A2:G2', 'Отчет по химическим исследованиям и экспериментам', title_format)
        worksheet.merge_range('A3:G3', 'Студент: Елфимова Каролина Александровна', title_format)
        worksheet.write('A4', f'Дата генерации: {datetime.now().strftime("%d.%m.%Y %H:%M")}', text_format)
        worksheet.write('A5', '', text_format)

        experiments = get_all_experiments_with_researchers() or []
        samples = get_all_samples() or []

        # Эксперименты
        start_row = 6
        worksheet.merge_range(f'A{start_row}:G{start_row}', 'ЭКСПЕРИМЕНТЫ', header_format)
        headers = ['ID', 'Название', 'Цель', 'Статус', 'Дата', 'Исследователь', 'Описание']
        for col, header in enumerate(headers):
            worksheet.write(start_row + 1, col, header, table_header_format)
        status_text_map = {'planned': 'Планирование', 'in_progress': 'В работе', 'completed': 'Завершен'}
        for row, exp in enumerate(experiments, start_row + 2):
            worksheet.write(row, 0, exp['id'], text_format)
            worksheet.write(row, 1, exp['name'], text_format)
            worksheet.write(row, 2, exp['purpose'], text_format)
            status_text = status_text_map.get(exp['status'], exp['status'])
            status_format = workbook.add_format({'border': 1, 'align': 'center'})
            if exp['status'] == 'completed':
                status_format.set_bg_color('#C6EFCE')
            elif exp['status'] == 'in_progress':
                status_format.set_bg_color('#FFEB9C')
            else:
                status_format.set_bg_color('#FFC7CE')
            worksheet.write(row, 3, status_text, status_format)
            worksheet.write(row, 4, exp['date'], text_format)
            worksheet.write(row, 5, exp['researcher'], text_format)
            worksheet.write(row, 6, exp['description'], text_format)
        worksheet.autofilter(f'A{start_row + 1}:G{start_row + 2 + len(experiments)}')

        # Образцы
        samples_start = start_row + 4 + len(experiments)
        worksheet.merge_range(f'A{samples_start}:G{samples_start}', 'ОБРАЗЦЫ', header_format)
        sample_headers = ['ID', 'Название', 'Хим. формула', 'Состояние', 'Масса (г)', 'Объем (мл)', 'Описание']
        for col, header in enumerate(sample_headers):
            worksheet.write(samples_start + 1, col, header, table_header_format)
        for row, sample in enumerate(samples, samples_start + 2):
            worksheet.write(row, 0, sample.id, text_format)
            worksheet.write(row, 1, sample.name, text_format)
            worksheet.write(row, 2, sample.chemical_formula, text_format)
            worksheet.write(row, 3, sample.aggregate_state, text_format)
            worksheet.write(row, 4, float(sample.mass) if sample.mass else 0, number_format)
            worksheet.write(row, 5, float(sample.volume) if sample.volume else 0, number_format)
            worksheet.write(row, 6, sample.description, text_format)
        worksheet.autofilter(f'A{samples_start + 1}:G{samples_start + 2 + len(samples)}')
        worksheet.freeze_panes(start_row + 1, 0)

    def create_analytics_sheet(self, workbook, header_format, title_format, table_header_format, number_format, text_format):
        worksheet = workbook.add_worksheet('Аналитика')
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)

        worksheet.merge_range('A1:E1', 'АНАЛИТИКА ДАННЫХ ЛАБОРАТОРИИ', title_format)

        experiments = get_all_experiments_with_researchers() or []
        samples = get_all_samples() or []
        measurements = get_all_measurements() or []

        # Метрики
        worksheet.merge_range('A3:E3', 'КЛЮЧЕВЫЕ МЕТРИКИ ПРОЕКТА', header_format)
        metrics = [
            ['Общее количество экспериментов:', len(experiments)],
            ['Общее количество образцов:', len(samples)],
            ['Общее количество измерений:', len(measurements)],
            ['Экспериментов завершено:', len([e for e in experiments if e['status'] == 'completed'])],
            ['Экспериментов в работе:', len([e for e in experiments if e['status'] == 'in_progress'])],
            ['Экспериментов планируется:', len([e for e in experiments if e['status'] == 'planned'])]
        ]
        for row, (label, value) in enumerate(metrics, 4):
            worksheet.write(f'A{row}', label, text_format)
            worksheet.write(f'B{row}', value, number_format)

        # Активность по дням
        activity_data = self._get_activity_by_date(experiments)
        if activity_data:
            dates, counts = zip(*activity_data)
            start_row = 12
            worksheet.write(f'A{start_row}', 'Активность по дням', header_format)
            for i, (date, count) in enumerate(activity_data, start_row + 1):
                worksheet.write(f'A{i}', date)
                worksheet.write(f'B{i}', count, number_format)

            chart = workbook.add_chart({'type': 'line'})
            chart.add_series({
                'name': 'Эксперименты',
                'categories': f'=Аналитика!$A${start_row + 1}:$A${start_row + len(dates)}',
                'values': f'=Аналитика!$B${start_row + 1}:$B${start_row + len(dates)}',
                'marker': {'type': 'circle', 'size': 6}
            })
            chart.set_title({'name': 'Активность по дням'})
            chart.set_x_axis({'name': 'Дата'})
            chart.set_y_axis({'name': 'Количество'})
            worksheet.insert_chart(f'D{start_row}', chart)

    def create_visualization_sheet(self, workbook, header_format, title_format):
        worksheet = workbook.add_worksheet('Визуализация')
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
        worksheet.merge_range('A1:B1', 'ВИЗУАЛИЗАЦИЯ ДАННЫХ ЛАБОРАТОРИИ', title_format)

        experiments = get_all_experiments_with_researchers() or []
        samples = get_all_samples() or []

        # Распределение по исследователям
        researcher_exp_count = {}
        for exp in experiments:
            r = exp['researcher']
            researcher_exp_count[r] = researcher_exp_count.get(r, 0) + 1
        row = 6
        worksheet.write('A5', 'Распределение экспериментов по исследователям', header_format)
        for researcher, count in researcher_exp_count.items():
            worksheet.write(f'A{row}', researcher[:20], header_format)
            worksheet.write(f'B{row}', count)
            row += 1

        if researcher_exp_count:
            chart1 = workbook.add_chart({'type': 'pie'})
            chart1.add_series({
                'categories': f'=Визуализация!$A$6:$A${5 + len(researcher_exp_count)}',
                'values': f'=Визуализация!$B$6:$B${5 + len(researcher_exp_count)}',
                'data_labels': {'percentage': True}
            })
            chart1.set_title({'name': 'По исследователям'})
            worksheet.insert_chart('D5', chart1)

        # Топ-5 исследователей
        top_researchers = sorted(researcher_exp_count.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_researchers:
            top_start = 20
            worksheet.write(f'A{top_start}', 'Топ-5 исследователей', header_format)
            for i, (r, c) in enumerate(top_researchers, top_start + 1):
                worksheet.write(f'A{i}', r[:20])
                worksheet.write(f'B{i}', c)
            chart2 = workbook.add_chart({'type': 'column'})
            chart2.add_series({
                'categories': f'=Визуализация!$A${top_start + 1}:$A${top_start + len(top_researchers)}',
                'values': f'=Визуализация!$B${top_start + 1}:$B${top_start + len(top_researchers)}',
                'data_labels': {'value': True}
            })
            chart2.set_title({'name': 'Активность'})
            worksheet.insert_chart(f'D{top_start}', chart2)

    def _get_activity_by_date(self, experiments):
        from datetime import datetime
        date_count = {}
        for exp in experiments:
            try:
                if exp['date'] != 'Не указана':
                    date_obj = datetime.strptime(exp['date'], '%d.%m.%Y')
                    date_str = date_obj.strftime('%d.%m')
                    date_count[date_str] = date_count.get(date_str, 0) + 1
            except:
                continue
        sorted_items = sorted(date_count.items(), key=lambda x: datetime.strptime(x[0], '%d.%m'))
        return sorted_items[-10:]
