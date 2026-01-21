from .connection import connect_db, close_db, database  
from .models import (
    Researcher, Experiment, Sample, Equipment, Method, Result,
    Measurement, Condition,
    ConductingAnExperiment, ExperimentalEquipment, SampleInExperiment
)
from peewee import fn
import datetime

def safe_db_operation(func):
    """Декоратор для безопасной работы с базой данных"""
    def wrapper(*args, **kwargs):
        try:
            connect_db()
            return func(*args, **kwargs)
        except Exception as e:
            print(f"DB Error in {func.__name__}: {e}")
            return None
        finally:
            close_db()
    return wrapper


# === RESEARCHER ===
@safe_db_operation
def get_all_researchers():
    return list(Researcher.select())

@safe_db_operation
def get_researcher_by_id(researcher_id):
    try:
        return Researcher.get_by_id(researcher_id)
    except Researcher.DoesNotExist:
        return None

@safe_db_operation
def update_researcher(researcher_id, **update_data):
    researcher = Researcher.get_by_id(researcher_id)
    for field, value in update_data.items():
        if hasattr(researcher, field):
            setattr(researcher, field, value)
    researcher.save()
    return True

@safe_db_operation
def delete_researcher(researcher_id):
    with database.atomic():
        # Удаляем связанные записи
        ConductingAnExperiment.delete().where(ConductingAnExperiment.researcher == researcher_id).execute()
        # Удаляем исследователя
        Researcher.delete_by_id(researcher_id)
    return True


# === EXPERIMENT ===
@safe_db_operation
def create_experiment(name, purpose, description="", plan="", status="planned", date_of_event=None, researcher_id=None):
    experiment = Experiment.create(
        name=name,
        purpose=purpose,
        description=description,
        plan=plan,
        status=status,
        date_of_event=date_of_event or datetime.date.today()
    )
    if researcher_id:
        ConductingAnExperiment.create(experiment=experiment.id, researcher=researcher_id)
    return experiment

@safe_db_operation
def get_all_experiments_with_researchers():
    experiments = []
    for exp in Experiment.select():
        researchers = (Researcher
                       .select()
                       .join(ConductingAnExperiment)
                       .where(ConductingAnExperiment.experiment == exp.id))
        main = f"{researchers[0].surname} {researchers[0].name}" if researchers else "Не указан"
        date_str = exp.date_of_event.strftime('%d.%m.%Y') if exp.date_of_event else 'Не указана'
        experiments.append({
            'id': exp.id,
            'name': exp.name,
            'purpose': exp.purpose,
            'status': exp.status,
            'date': date_str,
            'date_of_event': exp.date_of_event,
            'description': exp.description,
            'researcher': main
        })
    return experiments

@safe_db_operation
def get_my_experiments(researcher_id):
    experiments = (Experiment
                   .select()
                   .join(ConductingAnExperiment)
                   .where(ConductingAnExperiment.researcher == researcher_id))
    result = []
    for exp in experiments:
        date_str = exp.date_of_event.strftime('%d.%m.%Y') if exp.date_of_event else ''
        result.append({
            'id': exp.id,
            'name': exp.name,
            'purpose': exp.purpose,
            'status': exp.status,
            'date': date_str,
            'date_of_event': exp.date_of_event,
            'description': exp.description
        })
    return result

@safe_db_operation
def get_experiment_with_relations(experiment_id):
    try:
        exp = Experiment.get_by_id(experiment_id)
        researchers = list(Researcher.select().join(ConductingAnExperiment).where(ConductingAnExperiment.experiment == experiment_id))
        methods = list(Method.select().where(Method.experiment == experiment_id))
        samples = list(Sample.select().join(SampleInExperiment).where(SampleInExperiment.experiment == experiment_id))
        equipment = list(Equipment.select().join(ExperimentalEquipment).where(ExperimentalEquipment.experiment == experiment_id))
        results = list(Result.select().where(Result.experiment == experiment_id))
        conditions = list(Condition.select().where(Condition.experiment == experiment_id))
        
        # Получаем ID образцов, связанных с экспериментом
        sample_ids = [s.id for s in samples]
        # Получаем измерения для этих образцов
        measurements = list(Measurement.select().where(Measurement.sample.in_(sample_ids)))

        return {
            'experiment': exp,
            'researchers': researchers,
            'methods': methods,
            'samples': samples,
            'equipment': equipment,
            'results': results,
            'conditions': conditions,
            'measurements': measurements
        }
    except Exception as e:
        print(f"Ошибка загрузки эксперимента {experiment_id}: {e}")
        return None
        
        # Безопасное получение исследователей
        try:
            researchers = list(
                Researcher
                .select()
                .join(ConductingAnExperiment)
                .where(ConductingAnExperiment.experiment == experiment_id)
            )
        except Exception as e:
            print(f"Ошибка загрузки исследователей: {e}")
            researchers = []

        # Безопасное получение методов
        try:
            methods = list(Method.select().where(Method.experiment == experiment_id))
        except Exception as e:
            print(f"Ошибка загрузки методов: {e}")
            methods = []

        # Безопасное получение образцов
        try:
            samples = list(
                Sample
                .select()
                .join(SampleInExperiment)
                .where(SampleInExperiment.experiment == experiment_id)
            )
        except Exception as e:
            print(f"Ошибка загрузки образцов: {e}")
            samples = []

        # Безопасное получение оборудования
        try:
            equipment = list(
                Equipment
                .select()
                .join(ExperimentalEquipment)
                .where(ExperimentalEquipment.experiment == experiment_id)
            )
        except Exception as e:
            print(f"Ошибка загрузки оборудования: {e}")
            equipment = []

        # Безопасное получение результатов
        try:
            results = list(Result.select().where(Result.experiment == experiment_id))
        except Exception as e:
            print(f"Ошибка загрузки результатов: {e}")
            results = []

        # Безопасное получение условий
        try:
            conditions = list(Condition.select().where(Condition.experiment == experiment_id))
        except Exception as e:
            print(f"Ошибка при загрузке условий: {e}")
            import traceback
            traceback.print_exc()
            conditions = []

        # Безопасное получение измерений
        try:
            sample_ids = [s.id for s in samples]
            measurements = list(Measurement.select().where(Measurement.sample.in_(sample_ids)))
        except Exception as e:
            print(f"Ошибка загрузки измерений: {e}")
            measurements = []

        return {
            'experiment': exp,
            'researchers': researchers,
            'methods': methods,
            'samples': samples,
            'equipment': equipment,
            'results': results,
            'conditions': conditions,
            'measurements': measurements
        }
    except Experiment.DoesNotExist:
        print(f"Эксперимент с ID={experiment_id} не найден")
        return None
    except Exception as e:
        print(f"Критическая ошибка загрузки эксперимента {experiment_id}: {e}")
        import traceback
        traceback.print_exc()
        return None
        
@safe_db_operation
def update_experiment(experiment_id, **update_data):
    exp = Experiment.get_by_id(experiment_id)
    # Обновляем ВСЕ переданные поля
    for field, value in update_data.items():
        if hasattr(exp, field):
            setattr(exp, field, value)
    exp.save()
    return True

@safe_db_operation
def delete_experiment(experiment_id):
    with database.atomic():
        ConductingAnExperiment.delete().where(ConductingAnExperiment.experiment == experiment_id).execute()
        ExperimentalEquipment.delete().where(ExperimentalEquipment.experiment == experiment_id).execute()
        SampleInExperiment.delete().where(SampleInExperiment.experiment == experiment_id).execute()
        Method.delete().where(Method.experiment == experiment_id).execute()
        Result.delete().where(Result.experiment == experiment_id).execute()
        Condition.delete().where(Condition.experiment == experiment_id).execute()
        Experiment.delete_by_id(experiment_id)
    return True

@safe_db_operation
def get_experiment_by_id(experiment_id):
    try:
        return Experiment.get_by_id(experiment_id)
    except Experiment.DoesNotExist:
        return None

@safe_db_operation
def delete_experiment_completely(experiment_id):
    with database.atomic():
        # Удаляем связанные сущности
        ConductingAnExperiment.delete().where(ConductingAnExperiment.experiment == experiment_id).execute()
        SampleInExperiment.delete().where(SampleInExperiment.experiment == experiment_id).execute()
        ExperimentalEquipment.delete().where(ExperimentalEquipment.experiment == experiment_id).execute()
        Method.delete().where(Method.experiment == experiment_id).execute()
        Result.delete().where(Result.experiment == experiment_id).execute()
        Condition.delete().where(Condition.experiment == experiment_id).execute()
        
        # Измерения удаляем через образцы из эксперимента
        sample_ids = (SampleInExperiment
                      .select(SampleInExperiment.sample)
                      .where(SampleInExperiment.experiment == experiment_id))
        Measurement.delete().where(Measurement.sample.in_(sample_ids)).execute()
        
        Experiment.delete_by_id(experiment_id)
    return True
    
    

# === SAMPLE ===
@safe_db_operation
def create_sample_with_researcher(name, description, chemical_formula, aggregate_state, mass, volume, researcher_id):
    sample = Sample.create(
        name=name,
        description=description,
        chemical_formula=chemical_formula,
        aggregate_state=aggregate_state,
        mass=mass or 0.0,
        volume=volume or 0.0
    )
    # Находим или создаём эксперимент по умолчанию
    default_exp = (Experiment
                   .select()
                   .join(ConductingAnExperiment)
                   .where(ConductingAnExperiment.researcher == researcher_id)
                   .first())
    if not default_exp:
        default_exp = create_experiment(
            name=f"Эксперименты исследователя {researcher_id}",
            purpose="Общие эксперименты",
            status="in_progress",
            researcher_id=researcher_id
        )
    SampleInExperiment.create(experiment=default_exp.id, sample=sample.id)
    return sample

@safe_db_operation
def get_all_samples():
    return list(Sample.select())

@safe_db_operation
def get_my_samples(researcher_id):
    exp_ids = (Experiment
               .select(Experiment.id)
               .join(ConductingAnExperiment)
               .where(ConductingAnExperiment.researcher == researcher_id))
    samples = (Sample
               .select()
               .join(SampleInExperiment)
               .where(SampleInExperiment.experiment.in_(exp_ids)))
    return list(samples)

@safe_db_operation
def get_sample_by_id(sample_id):
    return Sample.get_by_id(sample_id)

@safe_db_operation
def update_sample(sample_id, **update_data):
    sample = Sample.get_by_id(sample_id)
    for field, value in update_data.items():
        if hasattr(sample, field):
            setattr(sample, field, value)
    sample.save()
    return True

@safe_db_operation
def delete_sample(sample_id):
    with database.atomic():
        SampleInExperiment.delete().where(SampleInExperiment.sample == sample_id).execute()
        Measurement.delete().where(Measurement.sample == sample_id).execute()
        Sample.delete_by_id(sample_id)
    return True

@safe_db_operation
def add_sample_to_experiment(experiment_id, sample_id):
    existing = SampleInExperiment.select().where(
        (SampleInExperiment.experiment == experiment_id) &
        (SampleInExperiment.sample == sample_id)
    ).first()
    if not existing:
        SampleInExperiment.create(experiment=experiment_id, sample=sample_id)
    return True

@safe_db_operation
def delete_sample_from_experiment(experiment_id, sample_id):
    SampleInExperiment.delete().where(
        (SampleInExperiment.experiment == experiment_id) &
        (SampleInExperiment.sample == sample_id)
    ).execute()
    return True


# === METHOD ===
@safe_db_operation
def get_method_by_id(method_id):
    try:
        return Method.get_by_id(method_id)
    except Method.DoesNotExist:
        return None
@safe_db_operation
def create_method(experiment_id, name, description):
    return Method.create(experiment=experiment_id, name=name, description=description)

@safe_db_operation
def update_method(method_id, name, description):
    method = Method.get_by_id(method_id)
    method.name = name
    method.description = description
    method.save()
    return True

@safe_db_operation
def delete_method(method_id):
    Method.delete_by_id(method_id)
    return True


# === EQUIPMENT ===
@safe_db_operation
def create_equipment(name, description):
    existing = Equipment.select().where(Equipment.name == name).first()
    if existing:
        return existing
    return Equipment.create(name=name, description=description)

@safe_db_operation
def update_equipment(equipment_id, **update_data):
    equip = Equipment.get_by_id(equipment_id)
    for field, value in update_data.items():
        if hasattr(equip, field):
            setattr(equip, field, value)
    equip.save()
    return True

@safe_db_operation
def delete_equipment(equipment_id):
    with database.atomic():
        ExperimentalEquipment.delete().where(ExperimentalEquipment.equipment == equipment_id).execute()
        Equipment.delete_by_id(equipment_id)
    return True

@safe_db_operation
def add_equipment_to_experiment(experiment_id, equipment_id):
    existing = ExperimentalEquipment.select().where(
        (ExperimentalEquipment.experiment == experiment_id) &
        (ExperimentalEquipment.equipment == equipment_id)
    ).first()
    if not existing:
        ExperimentalEquipment.create(experiment=experiment_id, equipment=equipment_id)
    return True

@safe_db_operation
def delete_equipment_from_experiment(experiment_id, equipment_id):
    ExperimentalEquipment.delete().where(
        (ExperimentalEquipment.experiment == experiment_id) &
        (ExperimentalEquipment.equipment == equipment_id)
    ).execute()
    return True


# === MEASUREMENT ===
@safe_db_operation
def create_measurement(sample_id, method, property_name, value, unit, accuracy, time_of_event):
    return Measurement.create(
        sample=sample_id,
        method=method,
        property=property_name,
        value=value,
        unit=unit,
        accuracy=accuracy,
        time_of_event=time_of_event
    )

@safe_db_operation
def update_measurement(measurement_id, **update_data):
    meas = Measurement.get_by_id(measurement_id)
    for field, value in update_data.items():
        if hasattr(meas, field):
            setattr(meas, field, value)
    meas.save()
    return True

@safe_db_operation
def delete_measurement(measurement_id):
    Measurement.delete_by_id(measurement_id)
    return True


# === CONDITION ===
@safe_db_operation
def create_condition(experiment_id, temperature=None, pressure=None, humidity=None, pH=None, illumination=None, duration=None):
    return Condition.create(
        experiment=experiment_id,
        temperature=temperature,
        pressure=pressure,
        humidity=humidity,
        pH=pH,
        illumination=illumination,
        duration=duration
    )
    
@safe_db_operation
def get_all_conditions():
    """
    Получает все условия с именами связанных экспериментов.
    Использует JOIN через Peewee ORM.
    """
    conditions = []
    query = (Condition
             .select(Condition, Experiment.name.alias('experiment_name'))
             .join(Experiment, on=(Condition.experiment == Experiment.id))
             .order_by(Experiment.name))
    for c in query:
        conditions.append({
            'id': c.id,
            'experiment_id': c.experiment.id,
            'experiment_name': c.experiment.name,
            'temperature': float(c.temperature) if c.temperature is not None else None,
            'pressure': float(c.pressure) if c.pressure is not None else None,
            'humidity': float(c.humidity) if c.humidity is not None else None,
            'pH': float(c.pH) if c.pH is not None else None,
            'illumination': c.illumination,
            'duration': c.duration
        })
    return conditions

@safe_db_operation
def update_condition(condition_id, **update_data):
    cond = Condition.get_by_id(condition_id)
    for field, value in update_data.items():
        if hasattr(cond, field):
            setattr(cond, field, value)
    cond.save()
    return True

@safe_db_operation
def delete_condition(condition_id):
    Condition.delete_by_id(condition_id)
    return True


# === RESULT ===
@safe_db_operation
def create_result(experiment_id, result_type, description, conclusions=None, url=None):
    return Result.create(
        experiment=experiment_id,
        type=result_type,
        description=description,
        conclusions=conclusions,
        URL=url
    )

@safe_db_operation
def update_result(result_id, **update_data):
    res = Result.get_by_id(result_id)
    for field, value in update_data.items():
        if hasattr(res, field):
            setattr(res, field, value)
    res.save()
    return True

@safe_db_operation
def delete_result(result_id):
    Result.delete_by_id(result_id)
    return True


# === SERVICE ===
@safe_db_operation
def get_current_researcher_id():
    researcher = Researcher.select().first()
    return researcher.id if researcher else 1

@safe_db_operation
def get_experiments_by_sample_id(sample_id):
    exps = (Experiment
            .select()
            .join(SampleInExperiment)
            .where(SampleInExperiment.sample == sample_id))
    return [{'id': e.id, 'name': e.name, 'status': e.status, 'date': e.date_of_event.strftime('%d.%m.%Y') if e.date_of_event else ''} for e in exps]

# ... предыдущие CRUD-функции ...

# === УДАЛЕНИЕ ===
@safe_db_operation
def delete_experiment(experiment_id):
    with database.atomic():
        ConductingAnExperiment.delete().where(ConductingAnExperiment.experiment == experiment_id).execute()
        ExperimentalEquipment.delete().where(ExperimentalEquipment.experiment == experiment_id).execute()
        SampleInExperiment.delete().where(SampleInExperiment.experiment == experiment_id).execute()
        Method.delete().where(Method.experiment == experiment_id).execute()
        Result.delete().where(Result.experiment == experiment_id).execute()
        Condition.delete().where(Condition.experiment == experiment_id).execute()
        Experiment.delete_by_id(experiment_id)
    return True

@safe_db_operation
def delete_sample_completely(sample_id):
    with database.atomic():
        SampleInExperiment.delete().where(SampleInExperiment.sample == sample_id).execute()
        Measurement.delete().where(Measurement.sample == sample_id).execute()
        Sample.delete_by_id(sample_id)
    return True

@safe_db_operation
def delete_method(method_id):
    Method.delete_by_id(method_id)
    return True

@safe_db_operation
def delete_equipment(equipment_id):
    with database.atomic():
        ExperimentalEquipment.delete().where(ExperimentalEquipment.equipment == equipment_id).execute()
        Equipment.delete_by_id(equipment_id)
    return True

@safe_db_operation
def delete_measurement(measurement_id):
    Measurement.delete_by_id(measurement_id)
    return True

@safe_db_operation
def delete_condition(condition_id):
    Condition.delete_by_id(condition_id)
    return True

@safe_db_operation
def delete_result(result_id):
    Result.delete_by_id(result_id)
    return True

@safe_db_operation
def delete_researcher(researcher_id):
    with database.atomic():
        ConductingAnExperiment.delete().where(ConductingAnExperiment.researcher == researcher_id).execute()
        Researcher.delete_by_id(researcher_id)
    return True
    
# === EQUIPMENT ===
@safe_db_operation
def get_all_equipment():
    return list(Equipment.select())

# === MEASUREMENTS ===
@safe_db_operation
def get_all_measurements():
    # Получаем измерения с именами образцов
    query = (Measurement
             .select(Measurement, Sample.name.alias('sample_name'))
             .join(Sample, on=(Measurement.sample == Sample.id))
             .order_by(Measurement.time_of_event.desc()))
    results = []
    for m in query:
        results.append({
            'id': m.id,
            'method': m.method,
            'property': m.property,
            'value': m.value,
            'unit': m.unit,
            'accuracy': m.accuracy,
            'time_of_event': m.time_of_event,
            'sample_name': m.sample.name
        })
    return results

# === METHODS ===
@safe_db_operation
def get_all_methods():
    query = (Method
             .select(Method, Experiment.name.alias('experiment_name'))
             .join(Experiment, on=(Method.experiment == Experiment.id))
             .order_by(Experiment.name))
    results = []
    for m in query:
        results.append({
            'id': m.id,
            'name': m.name,
            'description': m.description,
            'experiment_name': m.experiment.name
        })
    return results

# === RESULTS ===
@safe_db_operation
def get_all_results():
    query = (Result
             .select(Result, Experiment.name.alias('experiment_name'))
             .join(Experiment, on=(Result.experiment == Experiment.id))
             .order_by(Experiment.name))
    results = []
    for r in query:
        results.append({
            'id': r.id,
            'type': r.type,
            'description': r.description,
            'conclusions': r.conclusions,
            'experiment_name': r.experiment.name
        })
    return results

# === CONDITIONS ===
@safe_db_operation
def get_all_conditions():
    query = (Condition
             .select(Condition, Experiment.name.alias('experiment_name'))
             .join(Experiment, on=(Condition.experiment == Experiment.id))
             .order_by(Experiment.name))
    results = []
    for c in query:
        results.append({
            'id': c.id,
            'temperature': c.temperature,
            'pressure': c.pressure,
            'humidity': c.humidity,
            'pH': c.pH,
            'illumination': c.illumination,
            'duration': c.duration,
            'experiment_name': c.experiment.name
        })
    return results
    
@safe_db_operation
def get_researcher_stats():
    """Возвращает список исследователей с количеством экспериментов"""
    from .models import Researcher, ConductingAnExperiment
    query = (Researcher
             .select(Researcher.surname, Researcher.name,
                     fn.COUNT(ConductingAnExperiment.id).alias('experiment_count'))
             .join(ConductingAnExperiment, JOIN.LEFT_OUTER)
             .group_by(Researcher.id)
             .order_by(fn.COUNT(ConductingAnExperiment.id).desc()))
    return [
        {'surname': r.surname, 'name': r.name, 'experiment_count': r.experiment_count}
        for r in query
    ]

@safe_db_operation
def get_monthly_experiment_counts():
    """Возвращает словарь {месяц: количество} за последние 6 месяцев"""
    from .models import Experiment
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)
    query = (Experiment
             .select(fn.strftime('%Y-%m', Experiment.date_of_event).alias('month'),
                     fn.COUNT(Experiment.id).alias('count'))
             .where(Experiment.date_of_event >= six_months_ago)
             .group_by(fn.strftime('%Y-%m', Experiment.date_of_event))
             .order_by(fn.strftime('%Y-%m', Experiment.date_of_event)))
    result = {}
    for row in query:
        month = datetime.strptime(row.month, '%Y-%m').strftime('%b %Y')
        result[month] = row.count
    return result
    
@safe_db_operation
def delete_related_item(item_type, item_id):
    from .models import Method, Sample, Equipment, Result, Condition, Measurement
    try:
        if item_type == "method":
            Method.delete_by_id(item_id)
        elif item_type == "sample":
            # Удалить связь и сам образец (если не используется в других экспериментах)
            Sample.delete_by_id(item_id)
        elif item_type == "equipment":
            Equipment.delete_by_id(item_id)
        elif item_type == "result":
            Result.delete_by_id(item_id)
        elif item_type == "condition":
            Condition.delete_by_id(item_id)
        elif item_type == "measurement":
            Measurement.delete_by_id(item_id)
        return True
    except Exception as e:
        print(f"Ошибка удаления {item_type} {item_id}: {e}")
        return False
        
@safe_db_operation
def remove_sample_from_experiment(experiment_id, sample_id):
    # Удаляем связь из промежуточной таблицы
    SampleInExperiment.delete().where(
        (SampleInExperiment.experiment == experiment_id) &
        (SampleInExperiment.sample == sample_id)
    ).execute()
    return True

@safe_db_operation
def get_equipment_by_id(equipment_id):
    try:
        return Equipment.get_by_id(equipment_id)
    except Equipment.DoesNotExist:
        return None

@safe_db_operation
def update_equipment(equipment_id, **kwargs):
    equip = Equipment.get_by_id(equipment_id)
    for field, value in kwargs.items():
        if hasattr(equip, field):
            setattr(equip, field, value)
    equip.save()
    return True

@safe_db_operation
def create_equipment_and_link_to_experiment(experiment_id, name, description):
    # 1. Создаём оборудование
    equipment = Equipment.create(name=name, description=description)
    # 2. Привязываем к эксперименту
    ExperimentalEquipment.create(
        experiment=experiment_id,
        equipment=equipment.id
    )
    return True

@safe_db_operation
def remove_equipment_from_experiment(experiment_id, equipment_id):
    ExperimentalEquipment.delete().where(
        (ExperimentalEquipment.experiment == experiment_id) &
        (ExperimentalEquipment.equipment == equipment_id)
    ).execute()
    return True

@safe_db_operation
def get_measurement_by_id(measurement_id):
    try:
        return Measurement.get_by_id(measurement_id)
    except Measurement.DoesNotExist:
        return None

@safe_db_operation
def create_measurement_for_experiment(experiment_id, sample_id, method, property, value, unit, accuracy, time_of_event):
    Measurement.create(
        sample=sample_id,
        method=method,
        property=property,
        value=value,
        unit=unit,
        accuracy=accuracy,
        time_of_event=time_of_event
    )
    return True

@safe_db_operation
def update_measurement(measurement_id, **kwargs):
    m = Measurement.get_by_id(measurement_id)
    for field, value in kwargs.items():
        if hasattr(m, field):
            setattr(m, field, value)
    m.save()
    return True

@safe_db_operation
def delete_measurement(measurement_id):
    Measurement.delete_by_id(measurement_id)
    return True
    
@safe_db_operation
def get_samples_for_experiment(experiment_id):
    """Получает все образцы, привязанные к эксперименту"""
    samples = Sample.select().join(SampleInExperiment).where(SampleInExperiment.experiment == experiment_id)
    return list(samples)
    
# В crud.py

@safe_db_operation
def get_result_by_id(result_id):
    try:
        return Result.get_by_id(result_id)
    except Result.DoesNotExist:
        return None

@safe_db_operation
def create_result_for_experiment(experiment_id, **kwargs):
    Result.create(experiment=experiment_id, **kwargs)
    return True

@safe_db_operation
def update_result(result_id, **kwargs):
    r = Result.get_by_id(result_id)
    for field, value in kwargs.items():
        if hasattr(r, field):
            setattr(r, field, value)
    r.save()
    return True

@safe_db_operation
def delete_result(result_id):
    Result.delete_by_id(result_id)
    return True

@safe_db_operation
def get_condition_by_id(condition_id):
    try:
        return Condition.get_by_id(condition_id)
    except Condition.DoesNotExist:
        return None

@safe_db_operation
def create_condition_for_experiment(experiment_id, **kwargs):
    Condition.create(experiment=experiment_id, **kwargs)
    return True

@safe_db_operation
def update_condition(condition_id, **kwargs):
    c = Condition.get_by_id(condition_id)
    for field, value in kwargs.items():
        if hasattr(c, field):
            setattr(c, field, value)
    c.save()
    return True

@safe_db_operation
def delete_condition(condition_id):
    Condition.delete_by_id(condition_id)
    return True
