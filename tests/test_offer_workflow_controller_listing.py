from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from src.models import SwapRequest
from src.offer_workflow_service import (
    listar_requests_creados_desde_oferta_por_controlador,
    request_creado_desde_oferta_involucra_controlador,
)


def _crear_request(
    *,
    request_id: str,
    controlador_a: str,
    controlador_b: str,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
        },
    )


def test_request_creado_desde_oferta_involucra_controlador_si_es_controlador_a() -> None:
    request = _crear_request(
        request_id="req-1",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
    )

    assert request_creado_desde_oferta_involucra_controlador(
        request=request,
        controlador="ATC_001",
    ) is True


def test_request_creado_desde_oferta_involucra_controlador_si_es_controlador_b() -> None:
    request = _crear_request(
        request_id="req-1",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
    )

    assert request_creado_desde_oferta_involucra_controlador(
        request=request,
        controlador="ATC_002",
    ) is True


def test_request_creado_desde_oferta_involucra_controlador_devuelve_false_si_no_participa() -> None:
    request = _crear_request(
        request_id="req-1",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
    )

    assert request_creado_desde_oferta_involucra_controlador(
        request=request,
        controlador="ATC_999",
    ) is False


def test_request_creado_desde_oferta_involucra_controlador_rechaza_controlador_vacio() -> None:
    request = _crear_request(
        request_id="req-1",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
    )

    with pytest.raises(ValueError, match="controlador no puede estar vacio"):
        request_creado_desde_oferta_involucra_controlador(
            request=request,
            controlador="",
        )


def test_listar_requests_creados_desde_oferta_por_controlador_filtra_a_y_b(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    request_como_a = _crear_request(
        request_id="req-como-a",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
    )
    request_como_b = _crear_request(
        request_id="req-como-b",
        controlador_a="ATC_003",
        controlador_b="ATC_001",
    )
    request_no_participa = _crear_request(
        request_id="req-no-participa",
        controlador_a="ATC_004",
        controlador_b="ATC_005",
    )

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        lambda: [
            request_como_a,
            request_como_b,
            request_no_participa,
        ],
    )

    resultado = listar_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
    )

    assert [request.id for request in resultado] == [
        "req-como-a",
        "req-como-b",
    ]


def test_listar_requests_creados_desde_oferta_por_controlador_rechaza_controlador_vacio() -> None:
    with pytest.raises(ValueError, match="controlador no puede estar vacio"):
        listar_requests_creados_desde_oferta_por_controlador(
            controlador="",
        )


def test_listar_requests_creados_desde_oferta_por_controlador_no_evalua_no_decide_no_aplica(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    request = _crear_request(
        request_id="req-1",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
    )

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        lambda: [request],
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resultado = listar_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
    )

    assert resultado == [request]