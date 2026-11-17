import socket
import ssl
import time
import urllib.request
import ctypes
import logging
from datetime import datetime

# Konfiguration
PI_IP = "192.168.0.32"
TIMEOUT = 3.0  # Sekunden bis Timeout
LOG_FILE = r"C:\AdminScripts\pi_watchdog.log"

# Zu ueberwachende Dienste und Ports
SERVICES = {
    "SSH": 22,
    "HTTP (Nginx)": 80,
    "HTTPS (Nginx)": 443,
    "Samba (SMB)": 445
}

# Logging einrichten (schreibt in Datei und Konsole)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def check_tcp_port(ip: str, port: int) -> tuple[bool, float]:
    """Prueft per TCP-Handshake, ob ein Port offen ist, und misst die Latenz."""
    start = time.perf_counter()
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT):
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return True, latency_ms
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False, 0.0


def check_https_status(url: str) -> tuple[bool, int]:
    """Prueft, ob der Webserver HTTP 200 OK zurueckgibt (ignoriert Self-Signed Cert)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as response:
            return response.status == 200, response.status
    except Exception:
        return False, 0


def windows_alert(title: str, message: str):
    """Zeigt bei einem Ausfall ein natives Windows-Warnfenster an."""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x30 | 0x1000)


def run_checks():
    print(f"\n--- PI-LAB Watchdog Check ({datetime.now().strftime('%H:%M:%S')}) ---")
    failed_services = []

    for name, port in SERVICES.items():
        is_up, latency = check_tcp_port(PI_IP, port)
        if is_up:
            logging.info(f"OK   | {name:<15} (Port {port:<3}) erreichbar in {latency} ms")
        else:
            logging.error(f"FAIL | {name:<15} (Port {port:<3}) NICHT erreichbar!")
            failed_services.append(f"{name} (Port {port})")

    # Zusaetzlicher HTTP-Statuscode-Check fuer das Dashboard
    web_ok, status_code = check_https_status(f"https://{PI_IP}")
    if web_ok:
        logging.info(f"OK   | Web-Dashboard liefert HTTP {status_code}")
    else:
        logging.error(f"FAIL | Web-Dashboard antwortet nicht sauber (Status: {status_code})")
        failed_services.append("HTTPS Web-Dashboard")

    if failed_services:
        error_text = "Folgende Dienste auf PI-LAB sind ausgefallen:\n\n- " + "\n- ".join(failed_services)
        windows_alert("PI-LAB Server Alarm!", error_text)


if __name__ == "__main__":
    run_checks()
