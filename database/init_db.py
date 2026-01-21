# database/init_db.py
from models import db, Experiment, Sample, Measurement, Equipment, Result, Condition, Researcher

def create_tables():
    with db:
        db.create_tables([
            Researcher,
            Experiment,
            Sample,
            Equipment,
            Measurement,
            Result,
            Condition
        ])
    print("✅ Таблицы созданы!")

if __name__ == "__main__":
    create_tables()
