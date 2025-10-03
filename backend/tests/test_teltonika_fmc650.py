from app.integrations.teltonika_fmc650 import parse_teltonika_fmc650, FMC650_ALLOWED_IO

def test_basic_parse():
    ts, data = parse_teltonika_fmc650({
        "timestamp": "2025-01-01T00:00:00Z",
        "gps": {"lat": -33.4, "lon": -70.6, "speed": 12.3},
        "io": {"239": 1, "24": 65, "66": 12500, "9999": "xx"}
    })
    assert "gps" in data and data["gps"]["lat"] == -33.4
    assert "io" in data and data["io"]["Ignition"] == 1
    assert data["io"]["Speed"] == 65
    assert data["io"]["External Voltage"] == 12500
    assert data.get("rejected_io", {}).get("9999") == "xx"

def test_rejects_unknown_keeps_known():
    _, data = parse_teltonika_fmc650({"io": {"24": 50, "123456": 1}})
    assert "Speed" in data["io"]
    assert "123456" in data["rejected_io"]

def test_allowed_map_has_minimum_keys():
    for k in (239, 24, 66):
        assert k in FMC650_ALLOWED_IO
