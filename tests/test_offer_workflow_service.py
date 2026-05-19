from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from src.models import Controlador, SwapRequest
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_workflow_service import generar_oferta_y_crear_request


@dataclass(frozen=True)
class TurnoFake:
    codigo: str


@dataclass(frozen=True)
class AsignacionFake:
    fecha: str
    turno: TurnoFake
    controlador: Controlador | None


def _crear_asignaciones_fake() -> list[AsignacionFake]:
    return [
        AsignacionFake(
            fecha="2026-03-01",
            turno=TurnoFake("A"),
            controlador=Controlador("ATC_001"),
        ),
        AsignacionFake(
            fecha="2026-03-02",
            turno=TurnoFake("B"),
            controlador=Controlador("ATC_002"),
        ),
        AsignacionFake(
            fecha="2026-03-03",
            turno=TurnoFake("C"),
            controlador=Controlador("ATC_003"),
        ),
    ]


def _crear_oferta(
    *,
    posicion: int,
    idx_a: int,
    idx_b: int,
    clasificacion: str,
) -> OfertaEvaluada:
    return OfertaEvaluada(
        posicion=posicion,
        clasificacion=clasificacion,
        delta_score=0.0,
        delta_hard=0,
        delta_soft=0,
        idx_a=idx_a,
        idx_b=idx_b,
        evaluacion={
            "idx_a": idx_a,
            "idx_b": idx_b,
            "clasificacion": clasificacion,
            "delta_score": 0,
            "delta_hard": 0,
            "delta_soft": 0,
        },
    )


def _crear_reporte_fake() -> OfferReport:
    return OfferReport(
        mensaje="Mostrando mejores candidatos evaluados segun filtros actuales.",
        modo_exploracion="OFERTA_RAPIDA",
        ofertas=[
            _crear_oferta(
                posicion=1,
                idx_a=0,
                idx_b=1,
                clasificacion="BENEFICIOSO",
            ),
            _crear_oferta(
                posicion=2,
                idx_a=0,
                idx_b=2,
                clasificacion="ACEPTABLE",
            ),
        ],
        metadata={
            "modo_exploracion": "OFERTA_RAPIDA",
            "candidatos_generados": 20,
            "candidatos_prefiltrados": 12,
            "candidatos_seleccionados": 2,
            "candidatos_evaluados": 2,
            "top_n": 50,
            "criterio_seleccion": "candidate_selection_v1",
            "priorizacion_historica_aplicada": False,
            "roster_version_id_origen": "rv-1",
            "roster_hash_origen": "hash-1",
        },
    )


def _crear_request_fake() -> SwapRequest:
    return SwapRequest(
        id="req-workflow-selection",
        controlador_a="ATC_001",
        controlador_b="ATC_003",
        idx_a=0,
        idx_b=2,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo="CREADO_DESDE_OFERTA",
        roster_version_id="rv-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "offer_rank_observado": 2,
            "clasificacion_observada": "ACEPTABLE",
        },
    )


def test_generar_oferta_y_crear_request_combina_servicios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones_fake()
    reporte = _crear_reporte_fake()
    request = _crear_request_fake()

    llamadas_reporte = []
    llamadas_request = []

    def generar_oferta_fake(
        *,
        asignacion_origen: AsignacionFake,
        asignaciones: list[AsignacionFake],
        config_file: str,
        modo_exploracion: str,
        top_n: int,
        historial_controladores: dict[str, Any] | None,
        limite: int | None,
    ) -> OfferReport:
        llamadas_reporte.append(
            {
                "asignacion_origen": asignacion_origen,
                "asignaciones": asignaciones,
                "config_file": config_file,
                "modo_exploracion": modo_exploracion,
                "top_n": top_n,
                "historial_controladores": historial_controladores,
                "limite": limite,
            }
        )
        return reporte

    def crear_request_fake(
        *,
        reporte: OfferReport,
        posicion_oferta: int,
        asignaciones: list[AsignacionFake],
        config_file: str,
        roster_version_id_vigente: str | None,
        roster_hash_vigente: str | None,
    ) -> SwapRequest:
        llamadas_request.append(
            {
                "reporte": reporte,
                "posicion_oferta": posicion_oferta,
                "asignaciones": asignaciones,
                "config_file": config_file,
                "roster_version_id_vigente": roster_version_id_vigente,
                "roster_hash_vigente": roster_hash_vigente,
            }
        )
        return request

    monkeypatch.setattr(modulo, "generar_oferta_para_asignacion", generar_oferta_fake)
    monkeypatch.setattr(
        modulo,
        "crear_request_formal_desde_reporte_oferta",
        crear_request_fake,
    )

    resultado = generar_oferta_y_crear_request(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=2,
        modo_exploracion="OFERTA_RAPIDA",
        top_n=50,
        historial_controladores={"ATC_002": {"beneficios": 1}},
        limite_reporte=2,
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
    )

    assert llamadas_reporte == [
        {
            "asignacion_origen": asignaciones[0],
            "asignaciones": asignaciones,
            "config_file": "config_equilibrado.json",
            "modo_exploracion": "OFERTA_RAPIDA",
            "top_n": 50,
            "historial_controladores": {"ATC_002": {"beneficios": 1}},
            "limite": 2,
        }
    ]

    assert llamadas_request == [
        {
            "reporte": reporte,
            "posicion_oferta": 2,
            "asignaciones": asignaciones,
            "config_file": "config_equilibrado.json",
            "roster_version_id_vigente": "rv-1",
            "roster_hash_vigente": "hash-1",
        }
    ]

    assert resultado.reporte is reporte
    assert resultado.request is request
    assert resultado.request_id == "req-workflow-selection"
    assert resultado.cantidad_ofertas == 2


def test_generar_oferta_y_crear_request_usa_defaults_operativos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones_fake()
    reporte = _crear_reporte_fake()
    request = _crear_request_fake()

    parametros_recibidos = []

    def generar_oferta_fake(**kwargs: Any) -> OfferReport:
        parametros_recibidos.append(kwargs)
        return reporte

    monkeypatch.setattr(modulo, "generar_oferta_para_asignacion", generar_oferta_fake)
    monkeypatch.setattr(
        modulo,
        "crear_request_formal_desde_reporte_oferta",
        lambda **kwargs: request,
    )

    resultado = generar_oferta_y_crear_request(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=1,
    )

    assert parametros_recibidos[0]["modo_exploracion"] == "OFERTA_RAPIDA"
    assert parametros_recibidos[0]["top_n"] == 50
    assert parametros_recibidos[0]["historial_controladores"] is None
    assert parametros_recibidos[0]["limite"] is None
    assert resultado.request.estado == "PENDIENTE"


def test_generar_oferta_y_crear_request_no_evalua_no_decide_no_persiste(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones_fake()
    reporte = _crear_reporte_fake()
    request = _crear_request_fake()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_para_asignacion",
        lambda **kwargs: reporte,
    )
    monkeypatch.setattr(
        modulo,
        "crear_request_formal_desde_reporte_oferta",
        lambda **kwargs: request,
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe llamarse evaluacion, decision ni persistencia")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "guardar_request", prohibido, raising=False)

    resultado = generar_oferta_y_crear_request(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=1,
    )

    assert resultado.request.estado == "PENDIENTE"
    assert resultado.request.decision_sugerida is None


def test_generar_oferta_y_crear_request_propaga_error_de_posicion_invalida(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones_fake()
    reporte = _crear_reporte_fake()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_para_asignacion",
        lambda **kwargs: reporte,
    )

    def crear_request_fake(**kwargs: Any) -> SwapRequest:
        raise ValueError("No existe una oferta con posicion 99 en el reporte.")

    monkeypatch.setattr(
        modulo,
        "crear_request_formal_desde_reporte_oferta",
        crear_request_fake,
    )

    with pytest.raises(ValueError, match="No existe una oferta"):
        generar_oferta_y_crear_request(
            asignacion_origen=asignaciones[0],
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            posicion_oferta=99,
        )


def test_generar_oferta_y_crear_request_propaga_error_de_roster_obsoleto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones_fake()
    reporte = _crear_reporte_fake()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_para_asignacion",
        lambda **kwargs: reporte,
    )

    def crear_request_fake(**kwargs: Any) -> SwapRequest:
        raise ValueError("La oferta fue generada sobre otra version de roster.")

    monkeypatch.setattr(
        modulo,
        "crear_request_formal_desde_reporte_oferta",
        crear_request_fake,
    )

    with pytest.raises(ValueError, match="otra version de roster"):
        generar_oferta_y_crear_request(
            asignacion_origen=asignaciones[0],
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            posicion_oferta=1,
            roster_version_id_vigente="rv-2",
            roster_hash_vigente="hash-1",
        )