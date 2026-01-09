from pathlib import Path
import json

PROFILES = {
    "HTTP light": {
        "protocol": "HTTP",
        "rate": 5,
        "clients": 10,
        "target": "http://127.0.0.1:8080"
    },
    "HTTP medium": {
        "protocol": "HTTP",
        "rate": 20,
        "clients": 50,
        "target": "http://127.0.0.1:8080"
    },
    "HTTP heavy": {
        "protocol": "HTTP",
        "rate": 50,
        "clients": 100,
        "target": "http://127.0.0.1:8080"
    },

    "TCP light": {
        "protocol": "TCP",
        "rate": 10,
        "clients": 20,
        "target": "127.0.0.1",
        "port": 9000
    },
    "TCP stress": {
        "protocol": "TCP",
        "rate": 100,
        "clients": 200,
        "target": "127.0.0.1",
        "port": 9000
    },

    "UDP light": {
        "protocol": "UDP",
        "rate": 50,
        "clients": 50,
        "target": "127.0.0.1",
        "port": 9001
    },
    "UDP heavy": {
        "protocol": "UDP",
        "rate": 200,
        "clients": 300,
        "target": "127.0.0.1",
        "port": 9001
    },

    "TLS secure": {
        "protocol": "TLS",
        "rate": 10,
        "clients": 20,
        "target": "127.0.0.1",
        "port": 443
    },
    "TLS intense": {
        "protocol": "TLS",
        "rate": 50,
        "clients": 100,
        "target": "127.0.0.1",
        "port": 443
    },

    "WS chat": {
        "protocol": "WebSocket",
        "rate": 5,
        "clients": 20,
        "target": "ws://127.0.0.1:8765"
    },
    "WS real-time": {
        "protocol": "WebSocket",
        "rate": 20,
        "clients": 50,
        "target": "ws://127.0.0.1:8765"
    },
}

DYNAMIC_PROFILES = {
     "TCP Dynamic": {
        "protocol": "TCP",
        "rate_coef": (10, 100),        
        "clients_coef": (10, 200),
        "port": 9000,
        "target": "127.0.0.1",
        "update_interval": 5
    },
    "UDP Dynamic": {
        "protocol": "UDP",
        "rate_coef": (20, 300),
        "clients_coef": (10, 300),
        "port": 9001,
        "target": "127.0.0.1",
        "update_interval": 7
    },
    "TLS Dynamic": {
        "protocol": "TLS",
        "rate_coef": (5, 100),
        "clients_coef": (5, 200),
        "port": 443,
        "target": "127.0.0.1",
        "update_interval": 6
    },
    "HTTP Dynamic": {
        "protocol": "HTTP",
        "rate_coef": (2, 50),
        "clients_coef": (5, 100),
        "target": "http://127.0.0.1:8080",
        "port": 0,
        "update_interval": 10
    },
    "WebSocket Dynamic": {
        "protocol": "WebSocket",
        "rate_coef": (5, 50),
        "clients_coef": (5, 100),
        "target": "ws://127.0.0.1:8765",
        "port": 0,
        "update_interval": 8
    }
}

USER_PROFILES_FILE = Path("user_profiles.json")

def load_user_profiles():
    if USER_PROFILES_FILE.exists():
        data = json.loads(USER_PROFILES_FILE.read_text())
        return data.get("static", {}), data.get("dynamic", {})
    return {}, {}


def save_user_profiles(static_profiles, dynamic_profiles):
    data = {"static": static_profiles, "dynamic": dynamic_profiles}
    USER_PROFILES_FILE.write_text(json.dumps(data, indent=2))