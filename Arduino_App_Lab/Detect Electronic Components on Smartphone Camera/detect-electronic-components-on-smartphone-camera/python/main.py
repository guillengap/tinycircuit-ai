# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

import json
import ast
import secrets
import string
from datetime import datetime, UTC

from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import WebSocketCamera

# ---------- Pin config: Mapeo oficial de pines ----------
PIN_CONFIG = {
    # JDIGITAL
    "D21": {"active_low": False},
    "D20": {"active_low": False},
    "D13": {"active_low": False},
    "D12": {"active_low": False},
    "D11": {"active_low": False},
    "D10": {"active_low": False},
    "D9":  {"active_low": False},
    "D8":  {"active_low": False},
    "D7":  {"active_low": False},
    "D6":  {"active_low": False},
    "D5":  {"active_low": False},
    "D4":  {"active_low": False},  # Transistores
    "D3":  {"active_low": False},  # Capacitores
    "D2":  {"active_low": False},  # Resistencias
    "D1":  {"active_low": False},
    "D0":  {"active_low": False},
    # JANALOG
    "A0":  {"active_low": False},
    "A1":  {"active_low": False},
    "A2":  {"active_low": False},
    "A3":  {"active_low": False},
    "A4":  {"active_low": False},
    "A5":  {"active_low": False},
    # STM LEDS INTEGRADOS
    "LED3_R": {"active_low": True},
    "LED3_G": {"active_low": True},
    "LED3_B": {"active_low": True},
    "LED4_R": {"active_low": True},
    "LED4_G": {"active_low": True},
    "LED4_B": {"active_low": True},
}
PIN_NAMES = tuple(PIN_CONFIG.keys())

# Almacena estados lógicos (True = ON)
pin_states = {name: False for name in PIN_NAMES}

def _iso_now() -> str:
    return datetime.now(UTC).isoformat()

def _state_for_hw(name: str, logical_state: bool) -> bool:
    """Aplica inversión active-low según la configuración del hardware."""
    cfg = PIN_CONFIG.get(name, {})
    return (not logical_state) if cfg.get("active_low") else logical_state

def set_hardware_pin(name: str, logical_state: bool):
    """Función para actualizar el estado del pin vía Arduino Bridge."""
    if name not in PIN_NAMES:
        return
    
    pin_states[name] = logical_state
    hw_state = _state_for_hw(name, logical_state)
    
    try:
        Bridge.call("set_pin_by_name", name, hw_state)
    except Exception as e:
        print(f"[{_iso_now()}] Error cambiando pin {name}: {e}")

def reset_detection_pins():
    """Apaga las salidas asignadas a los componentes."""
    set_hardware_pin("D2", False)
    set_hardware_pin("D3", False)
    set_hardware_pin("D4", False)

# ---------- Configuración de Cámara e Interfaz Web ----------
def generate_secret() -> str:
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))

secret = generate_secret()

ui = WebUI()
resolution = (480, 640)
camera = WebSocketCamera(secret=secret, encrypt=True, resolution=resolution)
camera.on_status_changed(lambda evt_type, data: ui.send_message(evt_type, data))

detection = VideoObjectDetection(camera, confidence=0.5, debounce_sec=0.0)

ui.on_connect(lambda sid: ui.send_message("welcome", {
    "client_name": camera.name,
    "secret": secret,
    "status": camera.status,
    "protocol": camera.protocol,
    "ip": camera.ip,
    "port": camera.port
}))

ui.on_message("override_th", lambda sid, threshold: detection.override_threshold(threshold))

# ---------- Callback de Detección de Objetos ----------
def send_detections_to_ui(detections: dict):
    # Apagamos los pines al inicio de cada evaluación
    reset_detection_pins()

    for key, values in detections.items():
        label = key.lower()

        # Si el modelo detecta el componente con confianza suficiente:
        if len(values) > 0:
            if "resistor" in label or "resistencia" in label:
                set_hardware_pin("D2", True)
            elif "capacitor" in label:
                set_hardware_pin("D3", True)
            elif "transistor" in label:
                set_hardware_pin("D4", True)

        # Transmitir evento a la UI para renderizar las cajas delimitadoras
        for value in values:
            entry = {
                "content": key,
                "confidence": value.get("confidence"),
                "timestamp": _iso_now()
            }
            ui.send_message("detection", entry)

detection.on_detect_all(send_detections_to_ui)

def on_get_states():
    return {"timestamp": _iso_now(), "states": pin_states}

ui.expose_api("GET", "/states", on_get_states)

App.run()