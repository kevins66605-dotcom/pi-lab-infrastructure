import os
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# --- KONFIGURATION ---
PI_HOST = "admin@<PI_IP_ADRESSE>"
SMB_TARGET_ROOT = Path(r"\\<PI_IP_ADRESSE>\PiShare\WindowsBackups")
LOG_FILE = r"C:\AdminScripts\win_to_pi_backup.log"

# Ordner auf deinem Windows-PC, die gesichert werden sollen
SOURCE_FOLDERS = [
    Path(r"C:\AdminScripts"),
    Path(os.path.expandvars(r"%USERPROFILE%\Documents")),
]

# Ordner/Dateiendungen, die beim Backup uebersprungen werden sollen
IGNORE_NAMES = {".git", "__pycache__", "desktop.ini", "Thumbs.db"}
IGNORE_EXTS = {".log", ".tmp"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def is_pi_storage_mounted() -> bool:
    """Prueft per SSH, ob die 1TB-Platte auf dem Pi aktiv eingehaengt ist."""
    try:
        res = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", PI_HOST, "mountpoint -q /mnt/storage"],
            capture_output=True
        )
        return res.returncode == 0
    except Exception:
        return False


def sync_folder(src_dir: Path, dst_dir: Path) -> tuple[int, int]:
    """Kopiert nur neue oder geaenderte Dateien (inkrementelles Backup)."""
    copied = 0
    skipped = 0

    if not src_dir.exists():
        logging.warning(f"Quellordner existiert nicht (uebersprungen): {src_dir}")
        return 0, 0

    for root, dirs, files in os.walk(src_dir):
        # Ignorierte Unterordner (z.B. .git) gar nicht erst betreten
        dirs[:] = [d for d in dirs if d not in IGNORE_NAMES]

        rel_path = Path(root).relative_to(src_dir)
        target_sub_dir = dst_dir / rel_path
        target_sub_dir.mkdir(parents=True, exist_ok=True)

        for file_name in files:
            if file_name in IGNORE_NAMES or Path(file_name).suffix.lower() in IGNORE_EXTS:
                continue

            src_file = Path(root) / file_name
            dst_file = target_sub_dir / file_name

            try:
                # Pruefen, ob Datei schon existiert und identisch (Groesse + Zeitstempel) ist
                if dst_file.exists():
                    src_stat = src_file.stat()
                    dst_stat = dst_file.stat()
                    if src_stat.st_size == dst_stat.st_size and int(src_stat.st_mtime) <= int(dst_stat.st_mtime):
                        skipped += 1
                        continue

                shutil.copy2(src_file, dst_file)
                copied += 1
            except Exception as e:
                logging.error(f"Fehler beim Kopieren von {src_file}: {e}")

    return copied, skipped


def run_backup():
    start_time = datetime.now()
    logging.info("=== Starte Windows-zu-PI-LAB Backup ===")

    # 1. Sicherheits-Check: Ist die 1TB-Festplatte am Pi eingeschaltet?
    if not is_pi_storage_mounted():
        logging.warning("ABBRUCH: 1TB-Festplatte auf PI-LAB ist ausgeschaltet oder nicht eingehaengt.")
        return

    total_copied = 0
    total_skipped = 0

    for folder in SOURCE_FOLDERS:
        target_folder = SMB_TARGET_ROOT / folder.name
        logging.info(f"Synchronisiere '{folder}' -> '{target_folder}' ...")
        c, s = sync_folder(folder, target_folder)
        total_copied += c
        total_skipped += s

    duration = round((datetime.now() - start_time).total_seconds(), 1)
    logging.info(f"=== Fertig in {duration}s | Neu/Aktualisiert: {total_copied} | Unveraendert: {total_skipped} ===")


if __name__ == "__main__":
    run_backup()
