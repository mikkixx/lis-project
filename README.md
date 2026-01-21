# Лабораторная информационная система (LIS)

Система для управления химическими экспериментами, образцами, оборудованием и результатами.

## Особенности

- Управление экспериментами, образцами, оборудованием
- Генерация отчётов (Excel, PDF)
- Ролевая модель: просмотр чужих данных, редактирование только своих
- Интерфейс на PySide6
- База данных: MySQL через Peewee ORM

## Требования

- **OS**: Debian 11/12, Ubuntu 20.04+
- **Python**: 3.10+
- **MySQL**: 8.0+

## Установка

```bash
git clone https://github.com/mikkixx/lis-project.git
cd lis-project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env под вашу БД
nano .env
python main.py
