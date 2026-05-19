from __future__ import annotations

from datetime import datetime
from typing import Any

from src.engine import calcular_roster_hash
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.swap_service import crear_swap_request


SOURCE_TYPE_OFERTA_EVALUADA = "OFERTA_EVALUADA"
HISTORY_EVENT_CREADO_DESDE_OFERTA = "CREADO_DESDE_OFERTA"


def _validar_oferta_con_indices(oferta: OfertaEvaluada) -> None:
    if oferta.idx_a is None:
        raise ValueError("La oferta seleccionada no tiene idx_a.")

    if oferta.idx_b is None:
        raise ValueError("La oferta seleccionada no tiene idx_b.")


def _validar_indices_en_roster(
    *,
    oferta: OfertaEvaluada,
    asignaciones: list[Any],
) -> None:
    _validar_oferta_con_indices(oferta)

    assert oferta.idx_a is not None
    assert oferta.idx_b is not None

    if not (0 <= oferta.idx_a < len(asignaciones)):
        raise IndexError("idx_a de la oferta no es valido para el roster.")

    if not (0 <= oferta.idx_b < len(asignaciones)):
        raise IndexError("idx_b de la oferta no es valido para el roster.")


def _obtener_nombre_controlador(asignacion: Any, etiqueta: str) -> str:
    controlador = getattr(asignacion, "controlador", None)

    if controlador is None:
        raise ValueError(f"La asignacion {etiqueta} no tiene controlador asociado.")

    nombre = getattr(controlador, "nombre", None)

    if not nombre:
        raise ValueError(
            f"La asignacion {etiqueta} tiene controlador sin nombre valido."
        )

    return str(nombre)


def _validar_roster_version_origen(
    *,
    metadata: dict[str, Any],
    roster_version_id_vigente: str | None,
) -> None:
    roster_version_id_origen = metadata.get("roster_version_id_origen")

    if roster_version_id_origen is None:
        roster_version_id_origen = metadata.get("roster_version_id")

    if roster_version_id_origen is None:
        return

    if roster_version_id_vigente is None:
        return

    if roster_version_id_origen != roster_version_id_vigente:
        raise ValueError(
            "La oferta fue generada sobre otra version de roster. "
            "Regenerar ofertas antes de crear el request."
        )


def _validar_roster_hash_origen(
    *,
    metadata: dict[str, Any],
    roster_hash_vigente: str | None,
) -> None:
    roster_hash_origen = metadata.get("roster_hash_origen")

    if roster_hash_origen is None:
        roster_hash_origen = metadata.get("roster_hash")

    if roster_hash_origen is None:
        return

    if roster_hash_vigente is None:
        return

    if roster_hash_origen != roster_hash_vigente:
        raise ValueError(
            "La oferta fue generada sobre un roster distinto. "
            "Regenerar ofertas antes de crear el request."
        )


def _construir_offer_origin(
    *,
    oferta: OfertaEvaluada,
    metadata: dict[str, Any],
    roster_version_id_origen: str | None,
    roster_hash_origen: str | None,
    config_file_origen: str,
    selected_by: str | None = None,
    selection_reason: str | None = None,
    selection_note: str | None = None,
) -> dict[str, Any]:
    return {
        "created_from_offer": True,
        "source_type": SOURCE_TYPE_OFERTA_EVALUADA,
        "modo_exploracion": metadata.get("modo_exploracion"),
        "top_n": metadata.get("top_n"),
        "criterio_seleccion": metadata.get("criterio_seleccion"),
        "priorizacion_historica_aplicada": metadata.get(
            "priorizacion_historica_aplicada",
            False,
        ),
        "candidatos_generados": metadata.get("candidatos_generados"),
        "candidatos_prefiltrados": metadata.get("candidatos_prefiltrados"),
        "candidatos_seleccionados": metadata.get("candidatos_seleccionados"),
        "candidatos_evaluados": metadata.get("candidatos_evaluados"),
        "offer_rank_observado": oferta.posicion,
        "clasificacion_observada": oferta.clasificacion,
        "delta_score_observado": oferta.delta_score,
        "delta_hard_observado": oferta.delta_hard,
        "delta_soft_observado": oferta.delta_soft,
        "roster_version_id_origen": roster_version_id_origen,
        "roster_hash_origen": roster_hash_origen,
        "config_file_origen": config_file_origen,
        "selected_by": selected_by,
        "selection_reason": selection_reason,
        "selection_note": selection_note,
        "created_from_offer_at": datetime.now().isoformat(),
    }


def crear_request_formal_desde_oferta(
    *,
    oferta: OfertaEvaluada,
    asignaciones: list[Any],
    metadata: dict[str, Any],
    config_file: str = "config_equilibrado.json",
    roster_version_id_vigente: str | None = None,
    roster_hash_vigente: str | None = None,
    selected_by: str | None = None,
    selection_reason: str | None = None,
    selection_note: str | None = None,
) -> Any:
    _validar_indices_en_roster(
        oferta=oferta,
        asignaciones=asignaciones,
    )

    assert oferta.idx_a is not None
    assert oferta.idx_b is not None

    if roster_hash_vigente is None:
        roster_hash_vigente = calcular_roster_hash(asignaciones)

    roster_version_id_origen = metadata.get("roster_version_id_origen")
    if roster_version_id_origen is None:
        roster_version_id_origen = metadata.get("roster_version_id")

    roster_hash_origen = metadata.get("roster_hash_origen")
    if roster_hash_origen is None:
        roster_hash_origen = metadata.get("roster_hash")

    _validar_roster_version_origen(
        metadata=metadata,
        roster_version_id_vigente=roster_version_id_vigente,
    )
    _validar_roster_hash_origen(
        metadata=metadata,
        roster_hash_vigente=roster_hash_vigente,
    )

    asignacion_a = asignaciones[oferta.idx_a]
    asignacion_b = asignaciones[oferta.idx_b]

    controlador_a = _obtener_nombre_controlador(asignacion_a, "A")
    controlador_b = _obtener_nombre_controlador(asignacion_b, "B")

    request = crear_swap_request(
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=oferta.idx_a,
        idx_b=oferta.idx_b,
        motivo="CREADO_DESDE_OFERTA",
    )

    if request.estado != "PENDIENTE":
        raise ValueError(
            "El request creado desde oferta debe nacer en estado PENDIENTE."
        )

    request.offer_origin = _construir_offer_origin(
        oferta=oferta,
        metadata=metadata,
        roster_version_id_origen=roster_version_id_origen,
        roster_hash_origen=roster_hash_origen,
        config_file_origen=config_file,
        selected_by=selected_by,
        selection_reason=selection_reason,
        selection_note=selection_note,
    )

    seleccion_usuario = f", selected_by={selected_by}" if selected_by else ""

    request.add_history_entry(
        (
            f"{HISTORY_EVENT_CREADO_DESDE_OFERTA}: "
            f"source_type={SOURCE_TYPE_OFERTA_EVALUADA}, "
            f"offer_rank_observado={oferta.posicion}, "
            f"clasificacion_observada={oferta.clasificacion}"
            f"{seleccion_usuario}"
        )
    )

    return request

def obtener_oferta_por_posicion(
    *,
    reporte: OfferReport,
    posicion: int,
) -> OfertaEvaluada:
    if posicion <= 0:
        raise ValueError("La posicion de oferta debe ser mayor que cero.")

    for oferta in reporte.ofertas:
        if oferta.posicion == posicion:
            return oferta

    raise ValueError(
        f"No existe una oferta con posicion {posicion} en el reporte."
    )


def crear_request_formal_desde_reporte_oferta(
    *,
    reporte: OfferReport,
    posicion_oferta: int,
    asignaciones: list[Any],
    config_file: str = "config_equilibrado.json",
    roster_version_id_vigente: str | None = None,
    roster_hash_vigente: str | None = None,
    selected_by: str | None = None,
    selection_reason: str | None = None,
    selection_note: str | None = None,
) -> Any:
    oferta = obtener_oferta_por_posicion(
        reporte=reporte,
        posicion=posicion_oferta,
    )

    return crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=reporte.metadata,
        config_file=config_file,
        roster_version_id_vigente=roster_version_id_vigente,
        roster_hash_vigente=roster_hash_vigente,
        selected_by=selected_by,
        selection_reason=selection_reason,
        selection_note=selection_note,
    )