import os, json, time, logging
import requests
import paho.mqtt.client as mqtt

# --- Config ---
EMQX_HOST = os.getenv("EMQX_HOST", "emqx")
EMQX_PORT = int(os.getenv("EMQX_PORT", "1883"))

# Usa variables específicas para el worker; si no existen, cae a las antiguas EMQX_*
MQTT_USERNAME = os.getenv("MQTT_USERNAME") or os.getenv("EMQX_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD") or os.getenv("EMQX_PASSWORD", "")

MQTT_TOPIC = os.getenv("MQTT_TOPIC", "ingest/+")
API_BASE = os.getenv("API_BASE", "http://api:8000")
INGEST_URL = f"{API_BASE}/ingest/http"
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [mqtt-worker] %(message)s"
)
log = logging.getLogger("mqtt-worker")

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        log.info("Conectado a EMQX (%s:%s), suscribiendo a '%s'", EMQX_HOST, EMQX_PORT, MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        log.error("Error al conectar a EMQX, reason_code=%s", reason_code)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic  # ingest/<token>
        parts = topic.split("/", 1)
        if len(parts) != 2 or not parts[1]:
            log.warning("Tópico inválido '%s' (esperado ingest/<token>)", topic)
            return
        token = parts[1]
        raw = msg.payload.decode("utf-8") if msg.payload else "{}"
        payload = json.loads(raw or "{}")
        data = payload.get("data", payload if isinstance(payload, dict) else {})
        body = {"token": token, "data": data}
        if isinstance(payload, dict) and "ts" in payload:
            body["ts"] = payload["ts"]

        log.info("→ Ingest %s bytes topic=%s", len(msg.payload or b""), topic)
        r = requests.post(INGEST_URL, json=body, timeout=REQUEST_TIMEOUT)
        if r.status_code >= 300:
            log.error("API %s -> %s %s", INGEST_URL, r.status_code, r.text[:300])
        else:
            log.info("✔ Ingest OK device_id=%s", r.json().get("device_id"))
    except Exception as e:
        log.exception("Error procesando mensaje: %s", e)

def build_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    return client

if __name__ == "__main__":
    backoff = 1
    while True:
        try:
            c = build_client()
            log.info("Conectando a %s:%s ...", EMQX_HOST, EMQX_PORT)
            c.connect(EMQX_HOST, EMQX_PORT, keepalive=60)
            c.loop_forever(retry_first_connection=True)
        except Exception as e:
            log.error("Fallo de conexión a EMQX: %s (reintento en %ss)", e, backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

