# lis_project/reports/statistical_pdf_report.py
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class StatisticalPDFReport:
    def __init__(self):
        self.reports_dir = "./reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        self._register_fonts()

    def _register_fonts(self):
        """Регистрация шрифтов с поддержкой кириллицы"""
        font_paths = [
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
             '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
        ]
        for regular, bold in font_paths:
            if os.path.exists(regular) and os.path.exists(bold):
                pdfmetrics.registerFont(TTFont('CustomFont', regular))
                pdfmetrics.registerFont(TTFont('CustomFont-Bold', bold))
                self.font_name = 'CustomFont'
                return
        # Fallback
        self.font_name = 'Helvetica'

    def generate(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.reports_dir, f'статистический_отчет_{timestamp}.pdf')
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        styles = self._create_styles()
        story = []

        # === СТРАНИЦА 1: ТИТУЛЬНЫЙ ЛИСТ ===
        story.append(Paragraph("ЛАБОРАТОРНАЯ ИНФОРМАЦИОННАЯ СИСТЕМА", styles['title']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("Статистический отчет &laquo;Общая статистика приложения&raquo;", styles['heading']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['normal']))
        story.append(PageBreak())

        # === ЗАГРУЗКА ДАННЫХ ===
        stats = self._get_statistical_data()

        # === СТРАНИЦА 2: ОБЩАЯ СТАТИСТИКА ===
        story.append(Paragraph("1. Общая статистика", styles['heading']))
        story.append(Spacer(1, 15))

        # Таблица метрик
        metrics_table = Table([
            ["Показатель", "Значение"],
            ["Всего исследователей (пользователей)", str(stats['total_researchers'])],
            ["Всего экспериментов", str(stats['total_experiments'])],
            ["Всего образцов", str(stats['total_samples'])],
            ["Экспериментов за последние 30 дней", str(stats['last_30_days'])],
            ["Среднее количество экспериментов в месяц", f"{stats['avg_per_month']:.1f}"]
        ], colWidths=[3.5*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), self._get_bold_font()),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,1), (-1,-1), self.font_name),
            ('FONTSIZE', (0,1), (-1,-1), 10)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))

        # График активности
        activity_img = self._create_activity_chart(stats['activity_by_date'])
        if activity_img:
            story.append(Paragraph("График активности по дням (последние 30 дней)", styles['subheading']))
            story.append(Image(activity_img, width=6*inch, height=3*inch))

        story.append(PageBreak())

        # === СТРАНИЦА 3: АНАЛИЗ ДАННЫХ ===
        story.append(Paragraph("2. Анализ данных", styles['heading']))
        story.append(Spacer(1, 15))

        # Распределение по статусам
        status_pie = self._create_status_pie(stats['status_distribution'])
        if status_pie:
            story.append(Paragraph("Распределение экспериментов по статусам", styles['subheading']))
            story.append(Image(status_pie, width=4*inch, height=3*inch))
        story.append(Spacer(1, 15))

        # Топ-5 исследователей
        if stats['top_researchers']:
            top_data = [["Исследователь", "Экспериментов"]]
            for r in stats['top_researchers']:
                top_data.append([f"{r['surname']} {r['name'][0]}.", str(r['count'])])
            top_table = Table(top_data, colWidths=[2.5*inch, 1.5*inch])
            top_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.purple),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), self._get_bold_font()),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('FONTNAME', (0,1), (-1,-1), self.font_name)
            ]))
            story.append(Paragraph("Топ-5 наиболее активных исследователей", styles['subheading']))
            story.append(top_table)
        story.append(Spacer(1, 15))

        # Динамика по месяцам
        monthly_img = self._create_monthly_chart(stats['monthly_activity'])
        if monthly_img:
            story.append(Paragraph("Динамика добавления экспериментов по месяцам", styles['subheading']))
            story.append(Image(monthly_img, width=6*inch, height=3*inch))

        doc.build(story)
        return f"Статистический отчёт успешно создан: {filepath}"

    def _create_styles(self):
        styles = getSampleStyleSheet()
        return {
            'normal': ParagraphStyle(
                'NormalRU',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                leading=12
            ),
            'title': ParagraphStyle(
                'TitleRU',
                parent=styles['Heading1'],
                fontName=self._get_bold_font(),
                fontSize=18,
                alignment=1,
                spaceAfter=30
            ),
            'heading': ParagraphStyle(
                'HeadingRU',
                parent=styles['Heading2'],
                fontName=self._get_bold_font(),
                fontSize=14,
                spaceBefore=20,
                spaceAfter=12
            ),
            'subheading': ParagraphStyle(
                'SubheadingRU',
                parent=styles['Heading3'],
                fontName=self._get_bold_font(),
                fontSize=12,
                spaceBefore=12,
                spaceAfter=8
            )
        }

    def _get_bold_font(self):
        return 'CustomFont-Bold' if self.font_name == 'CustomFont' else 'Helvetica-Bold'

    def _get_statistical_data(self):
        """Получает все статистические данные через crud.py"""
        from database.crud import (
            get_all_researchers,
            get_all_experiments_with_researchers,
            get_researcher_stats,
            get_monthly_experiment_counts
        )
        from datetime import datetime

        researchers = get_all_researchers() or []
        experiments = get_all_experiments_with_researchers() or []

        # Общие метрики
        total_researchers = len(researchers)
        total_experiments = len(experiments)
        total_samples = sum(len(e.get('samples', [])) for e in experiments)

        # За последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        last_30_days = sum(
            1 for e in experiments
            if e['date'] != 'Не указана' and self._parse_date(e['date']) >= thirty_days_ago.date()
        )

        # Среднее в месяц (пример: за последние 90 дней → /3)
        ninety_days_ago = datetime.now() - timedelta(days=90)
        last_90_days = sum(
            1 for e in experiments
            if e['date'] != 'Не указана' and self._parse_date(e['date']) >= ninety_days_ago.date()
        )
        avg_per_month = last_90_days / 3 if last_90_days > 0 else 0

        # Активность по дням (последние 30 дней)
        activity_by_date = {}
        for e in experiments:
            if e['date'] != 'Не указана':
                d = self._parse_date(e['date'])
                if d >= thirty_days_ago.date():
                    activity_by_date[d.strftime('%d.%m')] = activity_by_date.get(d.strftime('%d.%m'), 0) + 1

        # Распределение по статусам
        status_distribution = {
            'Завершено': len([e for e in experiments if e['status'] == 'completed']),
            'В работе': len([e for e in experiments if e['status'] == 'in_progress']),
            'Планируется': len([e for e in experiments if e['status'] == 'planned'])
        }

        # Топ-5 исследователей
        researcher_stats = get_researcher_stats() or []
        top_researchers = sorted(researcher_stats, key=lambda x: x['experiment_count'], reverse=True)[:5]
        top_researchers = [{'surname': r['surname'], 'name': r['name'], 'count': r['experiment_count']} for r in top_researchers]

        # Динамика по месяцам (последние 6 месяцев)
        monthly_activity = get_monthly_experiment_counts() or {}

        return {
            'total_researchers': total_researchers,
            'total_experiments': total_experiments,
            'total_samples': total_samples,
            'last_30_days': last_30_days,
            'avg_per_month': avg_per_month,
            'activity_by_date': activity_by_date,
            'status_distribution': status_distribution,
            'top_researchers': top_researchers,
            'monthly_activity': monthly_activity
        }

    def _parse_date(self, date_str):
        from datetime import datetime
        try:
            return datetime.strptime(date_str, '%d.%m.%Y').date()
        except:
            return datetime.min.date()

    def _create_activity_chart(self, data):
        if not data:
            return None
        dates = sorted(data.keys(), key=lambda x: datetime.strptime(x, '%d.%m'))
        counts = [data[d] for d in dates]
        plt.figure(figsize=(8, 4))
        plt.plot(dates, counts, marker='o', linewidth=2, markersize=5)
        plt.title('Активность по дням')
        plt.xlabel('Дата')
        plt.ylabel('Количество экспериментов')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf

    def _create_status_pie(self, data):
        labels = list(data.keys())
        sizes = list(data.values())
        if not any(sizes):
            return None
        colors_list = ['#2ecc71', '#f39c12', '#e74c3c']
        plt.figure(figsize=(4, 4))
        plt.pie(sizes, labels=labels, colors=colors_list, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf

    def _create_monthly_chart(self, data):
        if not data:
            return None
        months = sorted(data.keys())
        counts = [data[m] for m in months]
        plt.figure(figsize=(8, 4))
        bars = plt.bar(months, counts, color='#3498db', alpha=0.8)
        plt.title('Динамика по месяцам')
        plt.xlabel('Месяц')
        plt.ylabel('Количество экспериментов')
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                     str(int(bar.get_height())), ha='center', va='bottom')
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf
