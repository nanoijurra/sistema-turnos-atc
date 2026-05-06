from src.exploration_modes import (
    CRITERIO_SELECCION_CANDIDATE_SELECTION_V1,
    MENSAJE_REPORTING_OFERTA_RAPIDA,
    ModoExploracion,
    construir_metadata_diagnostico_completo,
    construir_metadata_exhaustivo,
    construir_metadata_oferta_rapida,
)


def test_modos_oficiales_de_exploracion() -> None:
    assert ModoExploracion.OFERTA_RAPIDA.value == "OFERTA_RAPIDA"
    assert ModoExploracion.DIAGNOSTICO_COMPLETO.value == "DIAGNOSTICO_COMPLETO"
    assert ModoExploracion.EXHAUSTIVO.value == "EXHAUSTIVO"


def test_metadata_oferta_rapida_usa_candidate_selection_y_top_n_default() -> None:
    metadata = construir_metadata_oferta_rapida(
        candidatos_generados=100,
        candidatos_prefiltrados=80,
        candidatos_seleccionados=50,
        candidatos_evaluados=50,
        tiempos_por_etapa={
            "candidate_generation_ms": 10.5,
            "technical_prefilter_ms": 4.0,
            "candidate_selection_ms": 1.5,
            "simulator_ms": 120.0,
        },
    )

    assert metadata.modo_exploracion == "OFERTA_RAPIDA"
    assert metadata.candidatos_generados == 100
    assert metadata.candidatos_prefiltrados == 80
    assert metadata.candidatos_seleccionados == 50
    assert metadata.candidatos_evaluados == 50
    assert metadata.top_n == 50
    assert metadata.criterio_seleccion == CRITERIO_SELECCION_CANDIDATE_SELECTION_V1
    assert metadata.tiempos_por_etapa["simulator_ms"] == 120.0


def test_metadata_oferta_rapida_permita_top_n_parametrico() -> None:
    metadata = construir_metadata_oferta_rapida(
        candidatos_generados=100,
        candidatos_prefiltrados=80,
        candidatos_seleccionados=20,
        candidatos_evaluados=20,
        top_n=20,
    )

    assert metadata.top_n == 20
    assert metadata.candidatos_seleccionados == 20
    assert metadata.candidatos_evaluados == 20


def test_metadata_diagnostico_completo_no_usa_candidate_selection() -> None:
    metadata = construir_metadata_diagnostico_completo(
        candidatos_generados=100,
        candidatos_prefiltrados=80,
        candidatos_evaluados=80,
    )

    assert metadata.modo_exploracion == "DIAGNOSTICO_COMPLETO"
    assert metadata.candidatos_generados == 100
    assert metadata.candidatos_prefiltrados == 80
    assert metadata.candidatos_seleccionados == 80
    assert metadata.candidatos_evaluados == 80
    assert metadata.top_n is None
    assert metadata.criterio_seleccion is None


def test_metadata_exhaustivo_no_usa_prefiltro_ni_seleccion() -> None:
    metadata = construir_metadata_exhaustivo(
        candidatos_generados=30,
        candidatos_evaluados=30,
    )

    assert metadata.modo_exploracion == "EXHAUSTIVO"
    assert metadata.candidatos_generados == 30
    assert metadata.candidatos_prefiltrados == 30
    assert metadata.candidatos_seleccionados == 30
    assert metadata.candidatos_evaluados == 30
    assert metadata.top_n is None
    assert metadata.criterio_seleccion is None


def test_metadata_se_serializa_a_dict() -> None:
    metadata = construir_metadata_oferta_rapida(
        candidatos_generados=100,
        candidatos_prefiltrados=80,
        candidatos_seleccionados=40,
        candidatos_evaluados=40,
        top_n=40,
        tiempos_por_etapa={"total_ms": 250.0},
    )

    data = metadata.to_dict()

    assert data == {
        "modo_exploracion": "OFERTA_RAPIDA",
        "candidatos_generados": 100,
        "candidatos_prefiltrados": 80,
        "candidatos_seleccionados": 40,
        "candidatos_evaluados": 40,
        "top_n": 40,
        "criterio_seleccion": CRITERIO_SELECCION_CANDIDATE_SELECTION_V1,
        "tiempos_por_etapa": {"total_ms": 250.0},
    }


def test_mensaje_reporting_oferta_rapida_no_promete_todos_los_swaps_posibles() -> None:
    assert MENSAJE_REPORTING_OFERTA_RAPIDA == (
        "Mostrando mejores candidatos evaluados segun filtros actuales."
    )

    texto = MENSAJE_REPORTING_OFERTA_RAPIDA.lower()

    assert "todos los swaps posibles" not in texto
    assert "mejores candidatos evaluados" in texto