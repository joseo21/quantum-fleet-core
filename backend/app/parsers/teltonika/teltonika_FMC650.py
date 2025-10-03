from __future__ import annotations

import json
import os
from typing import Dict, Any, Tuple

# Ruta del JSON con los IDs válidos (mismo directorio)
_IDS_JSON = os.path.join(os.path.dirname(__file__), "ids_fmc650_min.json")

try:
    with open(_IDS_JSON, "r", encoding="utf-8") as f:
        _IDS_MAP: Dict[str, str] = json.load(f)
except Exception:
    _IDS_MAP = {}  # si falta el archivo, evita romper el import

_ALLOWED_IDS = set(int(k) for k in _IDS_MAP.keys())


def parse_io(raw_io: Dict[Any, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    - Acepta llaves como int o str
    - Devuelve (io_mapeado, rechazados)
      * io_mapeado -> {nombre_humano: valor}
      * rechazados -> {id_original: valor} (ids no soportados)
    """
    mapped: Dict[str, Any] = {}
    rejected: Dict[str, Any] = {}

    if not isinstance(raw_io, dict):
        return mapped, rejected

    for k, v in raw_io.items():
        try:
            kid = int(k)
        except Exception:
            rejected[str(k)] = v
            continue

        if kid in _ALLOWED_IDS:
            name = _IDS_MAP.get(str(kid), str(kid))
            mapped[name] = v
        else:
            rejected[str(kid)] = v

    return mapped, rejected
