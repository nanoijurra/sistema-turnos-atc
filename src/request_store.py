from src.models import SwapRequest


_REQUESTS: dict[str, SwapRequest] = {}


def guardar_request(request: SwapRequest) -> SwapRequest:
    """
    Guarda o actualiza un SwapRequest en memoria.
    """
    _REQUESTS[request.id] = request
    return request


def obtener_request(request_id: str) -> SwapRequest | None:
    """
    Devuelve un SwapRequest por id, o None si no existe.
    """
    return _REQUESTS.get(request_id)


def listar_requests() -> list[SwapRequest]:
    """
    Devuelve todos los SwapRequest almacenados en memoria.
    """
    return list(_REQUESTS.values())


def limpiar_requests() -> None:
    """
    Limpia el store en memoria. Útil para tests.
    """
    _REQUESTS.clear()