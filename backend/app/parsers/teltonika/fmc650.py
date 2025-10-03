from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, Any, Tuple

IDS_PATH = Path(__file__).with_name("ids_fmc650_min.json")

def to_snake(name: str) -> str:
    # "Engine RPM" -> "engine_rpm", "RS232_COM1Data" -> "rs232_com1_data"
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = s.replace("/", "_").replace("-", "_")
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-zA-Z0-9_]", "", s)
    return s.lower().strip("_")

class TeltonikaFMC650:
    """Normalizador: solo acepta IDs conocidos del FMC650 y los renombra a snake_case."""
    def __init__(self) -> None:
        if not IDS_PATH.exists():
            raise FileNotFoundError(f"No existe {IDS_PATH}")
        id2name: Dict[str, str] = json.loads(IDS_PATH.read_text(encoding="utf-8"))
        self.id2name = {str(k): v for k, v in id2name.items()}
        self.id2key  = {i: to_snake(n) for i, n in self.id2name.items()}

    def normalize_io(self, io: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        accepted: Dict[str, Any] = {}
        rejected: Dict[str, Any] = {}
        if not isinstance(io, dict):
            return {}, {"_invalid_io_container": io}
        for raw_id, value in io.items():
            sid = str(raw_id)
            key = self.id2key.get(sid)
            if not key:
                rejected[sid] = value
                continue
            accepted[key] = value  # aquí podrías validar tipos/rangos si lo necesitas
        return accepted, rejected

    def normalize_packet(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        out = {
            "device_external_id": payload.get("device_external_id"),
            "timestamp": payload.get("timestamp"),
            "gps": payload.get("gps") or {},
            "data": {},
            "rejected": {}
        }
        acc, rej = self.normalize_io(payload.get("io") or {})
        out["data"] = acc
        if rej:
            out["rejected"] = rej
        return out

# instancia para importar directo
teltonika_FMC650 = TeltonikaFMC650()
