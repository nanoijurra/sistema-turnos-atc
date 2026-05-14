from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.exploration_flow import ExplorationFlowResult
from src.offer_reporting import OfferReport


@dataclass(frozen=True)
class AsignacionFake:
    controlador: str
    fecha: str
    turno: str


def _crear_roster_fake() -> list[AsignacionFake]:
    return [
        AsignacionFake("ATC_001", "2026-03-01", "A"),
        AsignacionFake("ATC_002", "2026-03-02", "B"),
        AsignacionFake("ATC_003", "2026-03-03", "C"),
    ]


def _crear_resultado_flujo_fake() -> ExplorationFlowResult:
    return ExplorationFlowResult(
        modo_exploracion="OFERTA_RAPIDA",
        evaluaciones=[
            {
                "idx_a": 0,
                "idx_b": 1,
                "clasificacion": "ACEPTABLE",
                "delta_score": 0,
                "delta_hard": 0,
                "delta_soft": 0,
            },
            {
                "idx_a": 0,
                "idx_b": 2,
                "clasificacion": "BENEFICIOSO",
                "delta_score": 5,
                "delta_hard": 0,
                "delta_soft": -1,
            },
        ],
        metadata={
            "modo_exploracion": "OFERTA_RAPIDA",
            "candidatos_generados": 10,
            "candidatos_prefiltrados": 8,
            "candidatos_seleccionados": 2,
            "candidatos_evaluados": 2,
            "top_n": 50,
            "criterio_seleccion": "candidate_selection_v1",
            "priorizacion_historica_aplicada": False,
            "tiempos_por_etapa": {
                "total_ms": 12.5,
            },
        },
    )


def test_generar_oferta_para_asignacion_combina_flujo_y_reporte(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()
    resultado_flujo = _crear_resultado_flujo_fake()
    llamadas_flujo = []
    llamadas_reporte = []

    def explorar_fake(
        *,
        asignacion_origen: AsignacionFake,
        asignaciones: list[AsignacionFake],
        config_file: str,
        modo_exploracion: str,
        top_n: int,
        historial_controladores: dict[str, Any] | None,
    ) -> ExplorationFlowResult:
        llamadas_flujo.append(
            {
                "asignacion_origen": asignacion_origen,
                "asignaciones": asignaciones,
                "config_file": config_file,
                "modo_exploracion": modo_exploracion,
                "top_n": top_n,
                "historial_controladores": historial_controladores,
            }
        )
        return resultado_flujo

    def reporte_fake(
        resultado: ExplorationFlowResult,
        *,
        limite: int | None = None,
    ) -> OfferReport:
        llamadas_reporte.append(
            {
                "resultado": resultado,
                "limite": limite,
            }
        )

        from src.offer_reporting import generar_reporte_oferta

        return generar_reporte_oferta(resultado, limite=limite)

    monkeypatch.setattr(modulo, "explorar_candidatos_para_oferta", explorar_fake)
    monkeypatch.setattr(modulo, "generar_reporte_oferta", reporte_fake)

    reporte = modulo.generar_oferta_para_asignacion(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        modo_exploracion="OFERTA_RAPIDA",
        top_n=50,
        historial_controladores={"ATC_002": {"beneficios": 1}},
        limite=1,
    )

    assert llamadas_flujo == [
        {
            "asignacion_origen": asignaciones[0],
            "asignaciones": asignaciones,
            "config_file": "config_equilibrado.json",
            "modo_exploracion": "OFERTA_RAPIDA",
            "top_n": 50,
            "historial_controladores": {"ATC_002": {"beneficios": 1}},
        }
    ]

    assert llamadas_reporte == [
        {
            "resultado": resultado_flujo,
            "limite": 1,
        }
    ]

    assert reporte.modo_exploracion == "OFERTA_RAPIDA"
    assert reporte.cantidad_ofertas == 1
    assert reporte.metadata["top_n"] == 50


def test_generar_oferta_para_asignacion_usa_defaults_operativos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()
    resultado_flujo = _crear_resultado_flujo_fake()
    parametros_recibidos = []

    def explorar_fake(
        *,
        asignacion_origen: AsignacionFake,
        asignaciones: list[AsignacionFake],
        config_file: str,
        modo_exploracion: str,
        top_n: int,
        historial_controladores: dict[str, Any] | None,
    ) -> ExplorationFlowResult:
        parametros_recibidos.append(
            {
                "modo_exploracion": modo_exploracion,
                "top_n": top_n,
                "historial_controladores": historial_controladores,
            }
        )
        return resultado_flujo

    monkeypatch.setattr(modulo, "explorar_candidatos_para_oferta", explorar_fake)

    reporte = modulo.generar_oferta_para_asignacion(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
    )

    assert parametros_recibidos == [
        {
            "modo_exploracion": "OFERTA_RAPIDA",
            "top_n": 50,
            "historial_controladores": None,
        }
    ]

    assert reporte.modo_exploracion == "OFERTA_RAPIDA"


def test_generar_oferta_para_asignacion_permite_diagnostico_completo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()
    resultado_flujo = ExplorationFlowResult(
        modo_exploracion="DIAGNOSTICO_COMPLETO",
        evaluaciones=[
            {
                "idx_a": 0,
                "idx_b": 1,
                "clasificacion": "ACEPTABLE",
                "delta_score": 0,
                "delta_hard": 0,
                "delta_soft": 0,
            },
        ],
        metadata={
            "modo_exploracion": "DIAGNOSTICO_COMPLETO",
            "candidatos_generados": 10,
            "candidatos_prefiltrados": 8,
            "candidatos_seleccionados": 8,
            "candidatos_evaluados": 8,
            "top_n": None,
            "criterio_seleccion": None,
            "priorizacion_historica_aplicada": False,
            "tiempos_por_etapa": {
                "total_ms": 30.0,
            },
        },
    )

    def explorar_fake(
        *,
        asignacion_origen: AsignacionFake,
        asignaciones: list[AsignacionFake],
        config_file: str,
        modo_exploracion: str,
        top_n: int,
        historial_controladores: dict[str, Any] | None,
    ) -> ExplorationFlowResult:
        assert modo_exploracion == "DIAGNOSTICO_COMPLETO"
        return resultado_flujo

    monkeypatch.setattr(modulo, "explorar_candidatos_para_oferta", explorar_fake)

    reporte = modulo.generar_oferta_para_asignacion(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        modo_exploracion="DIAGNOSTICO_COMPLETO",
    )

    assert reporte.modo_exploracion == "DIAGNOSTICO_COMPLETO"
    assert reporte.metadata["modo_exploracion"] == "DIAGNOSTICO_COMPLETO"
    assert reporte.metadata["top_n"] is None


def test_generar_oferta_para_asignacion_no_decide_ni_persiste(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()
    resultado_flujo = _crear_resultado_flujo_fake()

    monkeypatch.setattr(
        modulo,
        "explorar_candidatos_para_oferta",
        lambda **kwargs: resultado_flujo,
    )

    reporte = modulo.generar_oferta_para_asignacion(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
    )

    data = reporte.to_dict()

    assert "decision_operativa" not in data
    assert "estado_request" not in data
    assert "persistido" not in data
    assert "aprobado" not in data
    assert "rechazado" not in data


def test_generar_oferta_para_asignacion_respeta_limite_de_reporte(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()
    resultado_flujo = _crear_resultado_flujo_fake()

    monkeypatch.setattr(
        modulo,
        "explorar_candidatos_para_oferta",
        lambda **kwargs: resultado_flujo,
    )

    reporte = modulo.generar_oferta_para_asignacion(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        limite=1,
    )

    assert reporte.cantidad_ofertas == 1


def test_generar_oferta_para_asignacion_propaga_error_de_limite_invalido(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()
    resultado_flujo = _crear_resultado_flujo_fake()

    monkeypatch.setattr(
        modulo,
        "explorar_candidatos_para_oferta",
        lambda **kwargs: resultado_flujo,
    )

    with pytest.raises(ValueError, match="limite debe ser mayor que cero"):
        modulo.generar_oferta_para_asignacion(
            asignacion_origen=asignaciones[0],
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            limite=0,
        )


def test_generar_oferta_para_asignacion_propaga_error_de_modo_no_soportado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_service as modulo

    asignaciones = _crear_roster_fake()

    def explorar_fake(**kwargs: Any) -> ExplorationFlowResult:
        raise ValueError("Modo de exploracion no soportado")

    monkeypatch.setattr(modulo, "explorar_candidatos_para_oferta", explorar_fake)

    with pytest.raises(ValueError, match="Modo de exploracion no soportado"):
        modulo.generar_oferta_para_asignacion(
            asignacion_origen=asignaciones[0],
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            modo_exploracion="EXHAUSTIVO",
        )