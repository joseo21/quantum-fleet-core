import os
import json
import pytest
import requests

API = os.environ.get("API", "http://localhost:8000")
TENANT = int(os.environ.get("TENANT", "1"))

pytestmark = pytest.mark.skipif(
    os.environ.get("E2E", "0") != "1",
    reason="Test E2E deshabilitado. Exporta E2E=1 para habilitarlo."
)

def _login_admin():
    r = requests.post(f"{API}/auth/login",
                      headers={"Content-Type":"application/x-www-form-urlencoded"},
                      data="username=admin@example.com&password=Admin123!")
    r.raise_for_status()
    return r.json()["access_token"]

def _get_device_token(admin_token):
    r = requests.get(f"{API}/devices",
                     headers={"Authorization": f"Bearer {admin_token}",
                              "X-Tenant-ID": str(TENANT)})
    r.raise_for_status()
    arr = r.json()
    assert isinstance(arr, list) and arr, "No hay devices en el tenant"
    return arr[0]["token"], arr[0]["external_id"]

def test_ingest_with_bearer_and_tenant():
    token = _login_admin()
    payload = {
        "device_external_id": "dev-dashboard-001",
        "timestamp": "2025-10-02T18:00:00Z",
        "gps": {"lat": -33.4, "lon": -70.6, "speed": 12.3},
        "io": {"239": 1, "24": 65, "66": 12500, "9999": "xx"}
    }
    r = requests.post(f"{API}/ingest/teltonika/FMC650",
                      headers={"Authorization": f"Bearer {token}",
                               "X-Tenant-ID": str(TENANT),
                               "Content-Type": "application/json"},
                      data=json.dumps(payload))
    r.raise_for_status()
    data = r.json()
    assert data["status"] == "ok"
    assert data["tenant_id"] == TENANT
    assert data["rejected_count"] >= 0

def test_ingest_with_device_token():
    admin_token = _login_admin()
    device_token, external_id = _get_device_token(admin_token)

    payload = {
        "gps": {"lat": -33.41, "lon": -70.61, "speed": 14.1},
        "io": {"239": 1, "24": 50, "66": 12345}
    }
    r = requests.post(f"{API}/ingest/teltonika/FMC650",
                      headers={"X-Tenant-ID": str(TENANT),
                               "X-Device-Token": device_token,
                               "Content-Type": "application/json"},
                      data=json.dumps(payload))
    r.raise_for_status()
    data = r.json()
    assert data["status"] == "ok"
    assert data["tenant_id"] == TENANT
    assert data["rejected_count"] == 0
