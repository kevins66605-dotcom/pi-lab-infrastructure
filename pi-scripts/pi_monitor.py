#!/usr/bin/env python3
import os
import shutil
import subprocess
from datetime import datetime

SERVICES = ["ssh", "nginx", "smbd", "fail2ban"]
HTML_OUTPUT = "/var/www/pi-lab/index.html"


def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read().strip()) / 1000.0, 1)
    except Exception:
        return "N/A"


def get_ram_usage():
    mem = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            parts = line.split(":")
            if len(parts) == 2:
                mem[parts[0].strip()] = int(parts[1].strip().split()[0])
    total_mb = round(mem.get("MemTotal", 0) / 1024, 1)
    avail_mb = round(mem.get("MemAvailable", 0) / 1024, 1)
    used_mb = round(total_mb - avail_mb, 1)
    percent = round((used_mb / total_mb) * 100, 1) if total_mb else 0
    return f"{used_mb} MB / {total_mb} MB ({percent}%)"


def get_disk_usage(path):
    if not os.path.ismount(path) and path != "/":
        return '<span style="color:#f9e2af;">Ausgeschaltet / Standby</span>'
    total, used, _ = shutil.disk_usage(path)
    total_gb = round(total / (1024**3), 1)
    used_gb = round(used / (1024**3), 1)
    percent = round((used / total) * 100, 1)
    return f"{used_gb} GB / {total_gb} GB ({percent}%)"


def check_service(service_name):
    res = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True,
        text=True
    )
    status = res.stdout.strip()
    color = "#a6e3a1" if status == "active" else "#f38ba8"
    return f'<span style="color:{color}; font-weight:bold;">{status.upper()}</span>'


def get_security_stats():
    """Liest Fail2ban-Status und offene TCP-Listening-Ports aus."""
    banned_info = "Keine aktiven Sperren"
    try:
        res = subprocess.run(
            ["sudo", "fail2ban-client", "status", "sshd"],
            capture_output=True,
            text=True
        )
        for line in res.stdout.splitlines():
            if "Currently banned" in line or "Total banned" in line:
                banned_info = line.strip()
    except Exception:
        banned_info = "Fail2ban Status nicht abrufbar"

    # Offene TCP-Ports zaehlen
    ports_res = subprocess.run(["ss", "-tln"], capture_output=True, text=True)
    listening_lines = [l for l in ports_res.stdout.splitlines() if "LISTEN" in l]
    return banned_info, len(listening_lines)


def build_html():
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    cpu_temp = get_cpu_temp()
    ram = get_ram_usage()
    sd_disk = get_disk_usage("/")
    hdd_disk = get_disk_usage("/mnt/storage")
    banned_info, open_ports = get_security_stats()

    service_rows = ""
    for srv in SERVICES:
        service_rows += f"<li><strong>{srv}:</strong> {check_service(srv)}</li>\n"

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <title>PI-LAB Live Monitor & Security</title>
    <style>
        body {{ font-family: sans-serif; background: #1e1e2e; color: #cdd6f4; text-align: center; padding: 30px; }}
        .box {{ background: #313244; padding: 30px; border-radius: 12px; display: inline-block; text-align: left; min-width: 380px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
        h1 {{ color: #89b4fa; margin-top: 0; }}
        h2 {{ color: #f9e2af; font-size: 1.05em; border-bottom: 1px solid #45475a; padding-bottom: 5px; margin-top: 20px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 8px 0; }}
        .footer {{ font-size: 0.8em; color: #a6adc8; margin-top: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="box">
        <h1>PI-LAB Server Dashboard</h1>
        <h2>Hardware & Storage</h2>
        <ul>
            <li><strong>CPU-Temperatur:</strong> {cpu_temp} °C</li>
            <li><strong>RAM-Auslastung:</strong> {ram}</li>
            <li><strong>SD-Karte (/):</strong> {sd_disk}</li>
            <li><strong>1TB Festplatte:</strong> {hdd_disk}</li>
        </ul>
        <h2>Systemd-Dienste</h2>
        <ul>
            {service_rows}
        </ul>
        <h2>Security Audit</h2>
        <ul>
            <li><strong>Fail2ban (SSH):</strong> {banned_info}</li>
            <li><strong>Offene TCP-Sockets:</strong> {open_ports} aktiv</li>
        </ul>
        <div class="footer">Letztes Update: {now} (Auto-Refresh: 60s)</div>
    </div>
</body>
</html>"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build_html()
    print("Dashboard & Security-Audit aktualisiert.")
