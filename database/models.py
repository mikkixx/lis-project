# lis_project/database/models.py
from peewee import *
from .connection import database

# Все модели наследуются напрямую от Model и используют глобальную database

class Researcher(Model):
    surname = CharField(max_length=100)
    name = CharField(max_length=100)
    patronymic = CharField(max_length=100, null=True)
    biography = TextField(null=True)
    academic_degree = CharField(max_length=100, null=True)
    organization = CharField(max_length=200)
    email = CharField(max_length=100)
    URL = CharField(max_length=200, null=True)

    class Meta:
        database = database
        table_name = 'researcher'

class Experiment(Model):
    name = CharField(max_length=200)
    purpose = CharField(max_length=500)
    description = TextField(null=True)
    plan = TextField(null=True)
    date_of_event = DateField(null=True)
    status = CharField(max_length=20)  # planned, in_progress, completed

    class Meta:
        database = database
        table_name = 'experiment'

class Sample(Model):
    name = CharField(max_length=200)
    description = TextField(null=True)
    chemical_formula = CharField(max_length=100, null=True)
    aggregate_state = CharField(max_length=100, null=True)
    mass = FloatField(null=True)
    volume = FloatField(null=True)

    class Meta:
        database = database
        table_name = 'sample'

class Equipment(Model):
    name = CharField(max_length=200)
    description = TextField(null=True)

    class Meta:
        database = database
        table_name = 'equipment'

class Method(Model):
    experiment = ForeignKeyField(Experiment, backref='methods')
    name = CharField(max_length=200)
    description = TextField(null=True)

    class Meta:
        database = database
        table_name = 'method'

class Result(Model):
    experiment = ForeignKeyField(Experiment, backref='results')
    type = CharField(max_length=100)
    description = TextField(null=True)
    conclusions = TextField(null=True)
    URL = CharField(max_length=255, null=True)

    class Meta:
        database = database
        table_name = 'result'

class Condition(Model):
    experiment = ForeignKeyField(Experiment, backref='conditions')
    temperature = DecimalField(max_digits=5, decimal_places=2)
    pressure = DecimalField(max_digits=6, decimal_places=2)
    humidity = DecimalField(max_digits=5, decimal_places=2)
    pH = DecimalField(max_digits=3, decimal_places=2)
    illumination = CharField(max_length=100)
    duration = DateTimeField()  # ← в дампе это TIMESTAMP, что в Python = datetime
    class Meta:
        database = database
        table_name = 'condition'

class Measurement(Model):
    sample = ForeignKeyField(Sample, backref='measurements')
    method = CharField(max_length=200)
    property = CharField(max_length=200)  # что измерялось
    value = FloatField()
    unit = CharField(max_length=50)
    accuracy = FloatField(null=True)
    time_of_event = DateTimeField(null=True)

    class Meta:
        database = database
        table_name = 'measurement'

# Связующие таблицы (многие-ко-многим)
class ConductingAnExperiment(Model):
    researcher = ForeignKeyField(Researcher, backref='experiments_conducted')
    experiment = ForeignKeyField(Experiment, backref='researchers_involved')

    class Meta:
        database = database
        table_name = 'conducting_an_experiment'

class SampleInExperiment(Model):
    sample = ForeignKeyField(Sample, backref='experiments_used_in')
    experiment = ForeignKeyField(Experiment, backref='samples_used')

    class Meta:
        database = database
        table_name = 'sample_in_experiment'

class ExperimentalEquipment(Model):
    equipment = ForeignKeyField(Equipment, backref='experiments_used_in')
    experiment = ForeignKeyField(Experiment, backref='equipment_used')

    class Meta:
        database = database
        table_name = 'experimental_equipment'
