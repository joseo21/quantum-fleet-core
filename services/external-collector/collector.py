import os, json, time, logging, re
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime, timezone

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("collector")

API_BASE = os.getenv("API_BASE", "http://api:8000")
INGEST_URL = f"{API_BASE}/ingest/teltonika/ingest"
STATE_FILE = os.getenv("STATE_FILE", "/data/state.json")  # persistencia simple
SOURCES_JSON = os.getenv("SOURCES_JSON", "")
SOURCES_FILE = os.getenv("SOURCES_FILE", "")

# Opcional: traducir IO por nombre → id Teltonika (si usas "name" en lugar de "id")
# Puedes llenar desde .env: IO_NAME_TO_ID='{"externalVoltage":"66","ignition":"239"}'
IO_NAME_TO_ID = json.loads(os.getenv("IO_NAME_TO_ID", "{}") or "{}")

def load_sources() -> List[Dict[str, Any]]:
    if SOURCES_FILE:
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return json.loads(content)
    if SOURCES_JSON:
        return json.loads(SOURCES_JSON)
    return []

def load_state() -> Dict[str, Any]:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.loads(f.read() or "{}")
    except Exception:
        return {}

def save_state(st: Dict[str, Any]):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(st, ensure_ascii=False, indent=2))

def env_expand(val: Any, source_state: Dict[str, Any]) -> Any:
    """Expande ${ENV} y ${state.*} en strings."""
    if isinstance(val, str):
        def repl(m):
            key = m.group(1)
            if key.startswith("state."):
                return str(source_state.get(key.split(".",1)[1], ""))
            return os.getenv(key, "")
        return re.sub(r"\$\{([^}]+)\}", repl, val)
    if isinstance(val, dict):
        return {k: env_expand(v, source_state) for k, v in val.items()}
    if isinstance(val, list):
        return [env_expand(v, source_state) for v in val]
    return val

def json_get(expr: str, ctx: Dict[str, Any], default=None):
    """Acceso simple por caminos tipo a.b.c (sin dependencias externas)."""
    if not expr:
        return default
    cur: Any = ctx
    for part in expr.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur

def to_ts_ms(val: Any, fmt: str) -> Optional[int]:
    if val is None:
        return None
    try:
        if fmt == "unix_ms":
            return int(val)
        if fmt == "unix_s":
            return int(val) * 1000
        if fmt == "iso8601":
            # Soporta "Z"
            s = str(val).replace("Z", "+00:00")
            return int(datetime.fromisoformat(s).timestamp() * 1000)
    except Exception:
        return None
    return None

def cast_value(val: Any, typ: Optional[str]):
    if val is None or typ is None:
        return val
    try:
        if typ == "int":
            return int(float(val))
        if typ == "float":
            return float(val)
        if typ == "str":
            return str(val)
        if typ == "bool":
            if isinstance(val, bool):
                return val
            s = str(val).strip().lower()
            return s in ("1","true","yes","on")
    except Exception:
        return None
    return val

def apply_transforms(rec: Dict[str, Any], transforms: List[Dict[str, Any]]):
    def get_path(d: Dict[str, Any], path: str):
        cur = d
        for p in path.split("."):
            if not isinstance(cur, dict) or p not in cur:
                return None, None
            parent = cur
            cur = cur[p]
        return parent, cur

    for t in transforms or []:
        op = t.get("op")
        path = t.get("path")
        parent, value = get_path(rec, path)
        if parent is None:
            continue
        if op == "round" and isinstance(value, (int, float)):
            nd = int(t.get("ndigits", 0))
            parent[path.split(".")[-1]] = round(value, nd)
        elif op == "clamp" and isinstance(value, (int, float)):
            mn = t.get("min", None)
            mx = t.get("max", None)
            if mn is not None and value < mn: value = mn
            if mx is not None and value > mx: value = mx
            parent[path.split(".")[-1]] = value

def build_io(mappings: List[Dict[str, Any]], item_ctx: Dict[str, Any]) -> Dict[str, Any]:
    io: Dict[str, Any] = {}
    for m in mappings or []:
        expr = m.get("expr")
        raw = eval_expr(expr, item_ctx)
        if raw is None:
            raw = m.get("default", None)
        val = cast_value(raw, m.get("cast"))
        if val is None:
            continue
        if "scale" in m and isinstance(val, (int, float)):
            val = val * float(m["scale"])
        key = None
        if "id" in m:
            key = str(m["id"])
        elif "name" in m:
            nm = str(m["name"])
            key = IO_NAME_TO_ID.get(nm, nm)  # si no hay mapping, usa el nombre tal cual
        if key:
            io[str(key)] = val
    return io

def eval_expr(expr: Optional[str], ctx: Dict[str, Any]):
    if not expr:
        return None
    # expr soporta: "response.x.y", "item.a.b", literales simples y backticks de template
    # Si expr empieza con "`${" lo evaluamos como f-string con ctx expandido (simple)
    try:
        if expr.startswith("`${") and expr.endswith("}`"):
            # ejemplo: "`${item.timestamp}-${item.lat}`"
            # resolvemos tokens ${...}
            def repl(m):
                inner = m.group(1)
                return str(json_get(inner, ctx, ""))
            s = re.sub(r"\$\{([^}]+)\}", repl, expr[1:-1])  # quitar backticks
            return s
        # ruta simple:
        if expr.startswith("response.") or expr.startswith("item."):
            return json_get(expr, ctx)
        # literal
        return expr
    except Exception:
        return None

def fetch_pages(session: requests.Session, src: Dict[str, Any], source_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    req = env_expand(src.get("request", {}), source_state)
    method = (req.get("method") or "GET").upper()
    url = req.get("url")
    headers = req.get("headers") or {}
    params = req.get("params") or {}
    body = req.get("body")
    timeout = float(req.get("timeout_sec", 15))
    pg = req.get("pagination", {"type":"none"})
    retry = req.get("retry", {"max_retries": 2, "backoff_sec": 2.0})
    max_retries = int(retry.get("max_retries", 2))
    backoff = float(retry.get("backoff_sec", 2.0))

    auth_cfg = req.get("auth", {"type":"none"})
    auth_type = auth_cfg.get("type", "none")
    auth = None
    if auth_type == "basic":
        auth = (auth_cfg["basic"]["username"], auth_cfg["basic"]["password"])
    elif auth_type == "bearer":
        headers["Authorization"] = f"Bearer {auth_cfg['token']}"

    pages: List[Dict[str, Any]] = []
    typ = (pg.get("type") or "none").lower()

    def do_request(u, p, b):
        for attempt in range(max_retries + 1):
            try:
                if method in ("GET","DELETE"):
                    r = session.request(method, u, params=p, headers=headers, timeout=timeout, auth=auth)
                else:
                    r = session.request(method, u, params=p, json=b, headers=headers, timeout=timeout, auth=auth)
                if 200 <= r.status_code < 300:
                    return r.json()
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(backoff * (attempt + 1))
                    continue
                log.error("HTTP %s %s -> %s %s", method, u, r.status_code, r.text[:200])
                return None
            except Exception as e:
                log.warning("Req error: %s (attempt %d)", e, attempt+1)
                time.sleep(backoff * (attempt + 1))
        return None

    if typ == "none":
        data = do_request(url, params, body)
        if data is not None:
            pages.append(data)
        return pages

    if typ == "page":
        cur = int(pg.get("page", pg.get("start", 1)))
        psize_param = pg.get("page_size_param")
        psize = pg.get("page_size", None)
        max_pages = int(pg.get("max_pages", 5))
        for _ in range(max_pages):
            p = dict(params)
            p[pg.get("param","page")] = cur
            if psize_param and psize:
                p[psize_param] = psize
            data = do_request(url, p, body)
            if data is None:
                break
            pages.append(data)
            # criterio de corte simple: si viene vacío
            records_expr = src["extract"].get("records_expr")
            arr = json_get(records_expr, {"response": data}, [])
            if not arr:
                break
            cur += 1
        return pages

    if typ == "cursor":
        nxt = None
        max_pages = int(pg.get("max_pages", 5))
        for i in range(max_pages):
            p = dict(params)
            if nxt:
                p[pg.get("param", "cursor")] = nxt
            data = do_request(url, p, body)
            if data is None:
                break
            pages.append(data)
            nxt_expr = pg.get("next_expr")
            nxt = eval_expr(nxt_expr, {"response": data}) if nxt_expr else None
            if not nxt:
                break
        return pages

    return pages

def process_source(src: Dict[str, Any], global_state: Dict[str, Any]):
    if not src.get("enabled", True):
        return

    src_id = src.get("id") or f"src-{hash(json.dumps(src))}"
    source_state = global_state.get(src_id, {})
    # Permite usar en params/body cosas como ${state.last_ts_iso}
    # Inicializa campos de estado comunes si no existen
    source_state.setdefault("last_ts", None)
    source_state.setdefault("last_ts_iso", None)
    source_state.setdefault("seen_keys", {})  # para dedupe

    session = requests.Session()
    pages = fetch_pages(session, src, source_state)

    ex = src.get("extract", {})
    records_expr = ex.get("records_expr")
    mappings = ex.get("mappings", {})
    filters = ex.get("filters", [])
    transforms = ex.get("transforms", [])

    # Resolver device para envío
    dev_cfg = src.get("device", {})
    dev_external_id = dev_cfg.get("external_id")
    dev_token = dev_cfg.get("token")
    # Si external_id viene de un campo:
    if isinstance(dev_external_id, dict) and "expr" in dev_external_id:
        # lo resolvemos por item más abajo
        dev_external_id_expr = dev_external_id["expr"]
        dev_external_id = None
    else:
        dev_external_id_expr = None

    batch_by_device: Dict[str, List[Dict[str, Any]]] = {}

    for data in pages:
        arr = json_get(records_expr, {"response": data}, [])
        if not isinstance(arr, list):
            log.warning("[%s] records_expr no devolvió una lista", src_id)
            continue

        for item in arr:
            ctx = {"response": data, "item": item}

            # filt
            passed = True
            for f in filters or []:
                expr = f.get("include_if")
                if expr:
                    val = eval_expr(expr, ctx)
                    truthy = bool(val) if not isinstance(val, bool) else val
                    if not truthy:
                        passed = False
                        break
            if not passed:
                continue

            # ts
            ts_cfg = mappings.get("ts")
            ts_ms = None
            if ts_cfg:
                ts_val = eval_expr(ts_cfg.get("expr"), ctx)
                ts_ms = to_ts_ms(ts_val, ts_cfg.get("format", "unix_ms"))
            if ts_ms is None:
                ts_ms = int(time.time() * 1000)

            # gps
            gps = {}
            for key in ("lat","lon","speed","sat","hdop"):
                g = mappings.get(f"gps.{key}")
                if g:
                    v = eval_expr(g.get("expr"), ctx)
                    v = cast_value(v, g.get("cast"))
                    if v is not None and isinstance(v, (int,float)) and "scale" in g:
                        v = v * float(g["scale"])
                    gps[key] = v
            if not gps:
                gps = None

            # io
            io = build_io(mappings.get("io", []), ctx)

            rec = {"ts": ts_ms}
            if gps: rec["gps"] = gps
            if io:  rec["io"] = io

            # transforms
            apply_transforms(rec, transforms)

            # dedupe (opcional)
            dd = src.get("state", {}).get("dedupe", {})
            key_expr = dd.get("key_expr")
            if key_expr:
                key = eval_expr(key_expr, ctx)
                if key:
                    if key in source_state["seen_keys"]:
                        continue
                    source_state["seen_keys"][key] = 1

            # resolver device_id de este item
            _external_id = dev_external_id
            _token = dev_token
            if dev_external_id_expr:
                _external_id = eval_expr(dev_external_id_expr, ctx)

            if not _external_id and not _token:
                log.warning("[%s] Record sin external_id/token; descarto", src_id)
                continue

            dev_key = f"ext:{_external_id}" if _external_id else f"tok:{_token}"
            batch_by_device.setdefault(dev_key, []).append(rec)

            # avanzar estado last_ts
            adv = src.get("state", {}).get("advance_last_ts")
            if adv and adv.get("from") == "ts":
                source_state["last_ts"] = max(int(source_state.get("last_ts") or 0), ts_ms)
                source_state["last_ts_iso"] = datetime.fromtimestamp(source_state["last_ts"]/1000.0, tz=timezone.utc).isoformat()

    # enviar por device
    for dev_key, batch in batch_by_device.items():
        body = {"batch": batch}
        if dev_key.startswith("ext:"):
            body["external_id"] = dev_key[4:]
        else:
            body["token"] = dev_key[4:]
        try:
            r = requests.post(INGEST_URL, json=body, timeout=10)
            if r.status_code >= 300:
                log.error("[%s] POST %s -> %s %s", src_id, INGEST_URL, r.status_code, r.text[:200])
        except Exception as e:
            log.exception("[%s] Error POST ingest: %s", src_id, e)

    # persistir estado
    global_state[src_id] = source_state

def main_loop():
    sources = load_sources()
    if not sources:
        log.warning("No hay fuentes configuradas (SOURCES_JSON/SOURCES_FILE).")
    state = load_state()

    # Pequeño scheduler simple por intervalo
    next_run: Dict[str, float] = {}
    while True:
        now = time.time()
        ran_any = False
        for src in sources:
            if not src.get("enabled", True):
                continue
            sid = src.get("id") or str(id(src))
            interval = int(src.get("interval_sec", 60))
            nr = next_run.get(sid, 0)
            if now >= nr:
                ran_any = True
                try:
                    process_source(src, state)
                except Exception:
                    log.exception("[%s] Error en process_source", sid)
                next_run[sid] = now + interval

        if ran_any:
            save_state(state)
        time.sleep(0.5)

if __name__ == "__main__":
    main_loop()
