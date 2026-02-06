# PROJECT: Jala-Viveka (Vedic-AI Logic)
# DEVELOPED BY: Namah Communication (MSME: UDYAM-AS-05-0000684)
# ARCHITECT: [JOYDEEP DAS]
# Improved: key persistence, robust Vedic multiply, logging, error handling

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

import requests
from cryptography.fernet import Fernet

# --- CONFIG & LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
LOGGER = logging.getLogger("jala-viveka")

KEY_ENV_VAR = "JALA_SHIELD_KEY"
KEY_FILE = Path.home() / ".jala_shield.key"

def load_or_create_key() -> bytes:
    """
    Load Fernet key from environment variable or key file.
    If not found, generate and persist to a user-only file (development convenience).
    For production, prefer supplying JALA_SHIELD_KEY via env or a secrets manager.
    """
    key = os.getenv(KEY_ENV_VAR)
    if key:
        LOGGER.debug("Loaded Fernet key from environment.")
        return key.encode()

    if KEY_FILE.exists():
        try:
            raw = KEY_FILE.read_bytes()
            LOGGER.debug(f"Loaded Fernet key from {KEY_FILE}")
            return raw.strip()
        except Exception as exc:
            LOGGER.warning("Failed to read key file: %s", exc)

    # Fallback: generate and persist (dev only)
    new_key = Fernet.generate_key()
    try:
        KEY_FILE.write_bytes(new_key)
        # Restrict file permissions where possible
        try:
            KEY_FILE.chmod(0o600)
        except Exception:
            pass
        LOGGER.warning("No Fernet key found; generated and stored key at %s (dev).", KEY_FILE)
    except Exception as exc:
        LOGGER.warning("Failed to persist generated key to file: %s. Still returning key in-memory.", exc)

    return new_key

KEY = load_or_create_key()
SHIELD = Fernet(KEY)


# --- VEDIC / UTILITY LOGIC ---
def nikhilam_multiply(a: int, b: int, base: int = 100) -> int:
    """
    A safe implementation of the 'Nikhilam' Vedic multiplication technique
    for numbers near a chosen base (e.g. 100). This implementation returns the product.
    It handles carries when the right part exceeds the base.

    Example: nikhilam_multiply(98, 97, base=100) -> 9506
    """
    if not all(isinstance(x, int) for x in (a, b, base)):
        raise TypeError("a, b and base must be integers")

    na = base - a
    nb = base - b
    left = a - nb
    right = na * nb

    # Handle carry-over from right-part exceeding the base
    if right >= base:
        carry = right // base
        right = right % base
        left += carry

    return left * base + right


def fetch_amrut_data(remote_url: Optional[str] = None, timeout: float = 5.0) -> Dict:
    """
    Fetch AMRUT data from an API if remote_url is provided, otherwise return simulated data.
    The requests call is guarded with timeout and exception handling; simulated fallback is used on failure.
    """
    if remote_url:
        LOGGER.info("Connecting to AMRUT API at %s ...", remote_url)
        try:
            resp = requests.get(remote_url, timeout=timeout)
            resp.raise_for_status()
            LOGGER.info("AMRUT API response received.")
            return resp.json()
        except Exception as exc:
            LOGGER.warning("Failed to fetch remote AMRUT data: %s. Falling back to simulation.", exc)

    # Simulated data (local testing / offline)
    LOGGER.info("Using simulated AMRUT data (offline).")
    time.sleep(0.5)
    return {"zone": "Guwahati-East", "ph": 7.2, "flow_rate": 85, "leakage": False}


def evaluate_viveka(data: Dict) -> Tuple[str, str]:
    """
    Decision logic based on flow_rate and other metrics.
    Returns (status_label, recommended_action).
    """
    flow = data.get("flow_rate")
    if flow is None:
        raise ValueError("Missing flow_rate in data")

    try:
        flow = float(flow)
    except Exception:
        raise ValueError("flow_rate must be numeric")

    if flow >= 80:
        return "SATTVIC (Optimal)", "Maintain Pressure"
    elif 40 <= flow < 80:
        return "RAJASIC (High Demand)", "Activate Auxiliary Pumps"
    else:
        return "TAMASIC (Low/Leak)", "Trigger SUDDHI (Emergency Shutdown)"


def encrypt_report(report_bytes: bytes) -> bytes:
    """Encrypt bytes with the shared Fernet instance."""
    return SHIELD.encrypt(report_bytes)


def decrypt_report(token: bytes) -> bytes:
    """Decrypt bytes with the shared Fernet instance."""
    return SHIELD.decrypt(token)


# --- MAIN COMMAND CENTER ---
def run_system(remote_url: Optional[str] = None):
    LOGGER.info("--- JALA-VIVEKA: AMRUT 2.0 PROTOCHART ---")
    data = fetch_amrut_data(remote_url=remote_url)
    status, action = evaluate_viveka(data)

    LOGGER.info("ZONE: %s", data.get("zone"))
    LOGGER.info("ANALYSIS: %s", status)
    LOGGER.info("COMMAND: %s", action)

    # Encrypting report for Government submission
    report_str = json.dumps({"zone": data.get("zone"), "status": status, "action": action})
    protected_report = encrypt_report(report_str.encode())
    LOGGER.info("[SHIELD]: Encrypted Report (sample): %s...", protected_report[:20])


if __name__ == "__main__":
    # For development run with: python jalaviveka.py
    # To test remote endpoint: set REMOTE_AMRUT_URL env var or pass it below.
    remote_url = os.getenv("REMOTE_AMRUT_URL")
    run_system(remote_url=remote_url)
