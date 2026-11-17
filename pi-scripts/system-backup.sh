#!/bin/bash

BACKUP_DIR="/mnt/storage/backups"
PASS_FILE="/etc/backup-keys/backup.pass"
DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_FILE="$BACKUP_DIR/pi-config-backup-$DATE.tar.gz.enc"

# Pruefen, ob Festplatte eingehaengt ist
if ! ls "$BACKUP_DIR" >/dev/null 2>&1; then
    echo "Abbruch: Festplatte ist aktuell ausgeschaltet."
    exit 1
fi

# Packen UND direkt per Stream mit AES-256 verschluesseln (keine unverschluesselte Zwischendatei!)
tar -cz /etc/samba /etc/ssh /etc/fail2ban /etc/ufw /etc/fstab /etc/nginx /etc/ssl/homelab-ca /home/admin/scripts 2>/dev/null | \
  openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:"$PASS_FILE" -out "$BACKUP_FILE"

# Alte unverschluesselte und aeltere verschluesselte Backups (> 14 Tage) aufraeumen
rm -f "$BACKUP_DIR"/*.tar.gz
find "$BACKUP_DIR" -name "pi-config-backup-*.tar.gz.enc" -type f -mtime +14 -delete

echo "Verschluesseltes Backup erfolgreich erstellt: $BACKUP_FILE"
