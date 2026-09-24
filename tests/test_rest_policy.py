from datetime import date, time
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from src.models import Asignacion, Turno, crear_esquema_8h
from src.validator import validar_descanso_minimo
from src.roster_day_timeline import RosterDiaImportado, RosterDayStatus
from src.roster_timeline_validator import validar_descanso_minimo_timeline, validar_timeline_importada
from src.engine import ejecutar_regla, cargar_config
from src.technical_prefilter import _obtener_horas_minimas_descanso
from src.rest_policy import rest_hours_from_parameters


def pair(code1='A', code2='A'):
    scheme = crear_esquema_8h()
    assignments = [Asignacion(date(2026, 6, d), scheme.obtener_turno(c)) for d, c in [(1, code1), (2, code2)]]
    days = [RosterDiaImportado(controlador='TEST', fecha=a.fecha, estado=RosterDayStatus.OPERATIVO,
            raw_value=a.turno.codigo, codigo=a.turno.codigo, codigo_normalizado=a.turno.codigo) for a in assignments]
    return assignments, days


@pytest.mark.parametrize('first,second,hours,invalid', [('B','A',8,True),('A','A',16,False),('A','B',24,False),('C','A',0,True)])
def test_default_agreement(first, second, hours, invalid):
    assignments, days = pair(first, second)
    for violations in [validar_descanso_minimo(assignments), validar_descanso_minimo_timeline(days), validar_timeline_importada(days)]:
        rest = [v for v in violations if 'DESCANSO' in v.codigo]
        assert bool(rest) == invalid
        if invalid:
            assert rest[0].metadata['horas_descanso'] == hours
            assert rest[0].metadata['horas_minimas'] == 16


@pytest.mark.parametrize('minutes,invalid', [(29,True),(30,False),(31,False)])
def test_traditional_minute_boundary(minutes, invalid):
    assignments, _ = pair()
    assignments[1] = Asignacion(date(2026,6,2), Turno('X',time(6,minutes),8,'TEST'))
    assert bool(validar_descanso_minimo(assignments)) == invalid


@pytest.mark.parametrize('threshold,invalid', [(15.99,False),(16,False),(16.01,True)])
def test_timeline_exact_configurable_boundary(threshold, invalid):
    assignments, days = pair()
    assert bool(validar_descanso_minimo_timeline(days, threshold)) == invalid
    assert bool(validar_descanso_minimo(assignments, threshold)) == invalid


@pytest.mark.parametrize('parameters', [{}, {'horas_minimas':20}, {'min_horas':20}, {'min_horas':20,'horas_minimas':20}])
def test_engine_prefilter_same_parameter_contract(parameters):
    assignments, _ = pair()
    rule = {'nombre':'Descanso','funcion':'validar_descanso_minimo','prioridad':1,'parametros':parameters}
    expected = 20 if parameters else 16
    with patch('src.technical_prefilter.cargar_config', return_value={'reglas':[rule]}):
        assert _obtener_horas_minimas_descanso() == expected
    result = ejecutar_regla(assignments,rule)
    assert bool(result.violaciones) == (expected > 16)
    if result.violaciones:
        assert result.violaciones[0].metadata['horas_minimas'] == expected


@pytest.mark.parametrize('parameters', [{'min_horas':12,'horas_minimas':16},{'horas_minima':16},{'horas_minimas':True},{'min_horas':0},{'horas_minimas':-1},{'horas_minimas':float('nan')},{'horas_minimas':float('inf')},{'min_horas':'16'}])
def test_bad_parameters_fail_in_engine_and_prefilter(parameters):
    rule = {'nombre':'Descanso','funcion':'validar_descanso_minimo','prioridad':1,'parametros':parameters}
    with pytest.raises(ValueError): ejecutar_regla([],rule)
    with patch('src.technical_prefilter.cargar_config', return_value={'reglas':[rule]}):
        with pytest.raises(ValueError): _obtener_horas_minimas_descanso()


@pytest.mark.parametrize('filename',['config_equilibrado.json','config_restrictivo.json','config_flexible.json'])
def test_shipped_profiles_keep_hard_rest_minimum(filename):
    config = cargar_config(filename)
    rule = next(r for r in config['reglas'] if r['funcion']=='validar_descanso_minimo')
    assert rule['parametros'] == {'horas_minimas':16}
    assert _obtener_horas_minimas_descanso(filename) == 16
    assert ejecutar_regla(pair('B','A')[0],rule).violaciones


def test_root_config_and_operational_window():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root/'config.json').read_text())
    rule = next(r for r in config['reglas'] if r['funcion']=='validar_descanso_minimo')
    assert rest_hours_from_parameters(rule['parametros']) == 16
    assert cargar_config()['operacion']['horas_minimas_antes_del_turno_para_permitir_swap'] == 12
