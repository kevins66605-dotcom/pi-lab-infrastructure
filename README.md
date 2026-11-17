\[Deutsch](README.md) | \[English](README.en.md)



\# PI-LAB Home-Lab Infrastructure \& Automation



Dieses Repository dokumentiert den Aufbau, das Security-Hardening, das Monitoring sowie die Automatisierung meiner lokalen Linux-Server-Infrastruktur auf einem \*\*Raspberry Pi 1 Model B+ (700 MHz Single-Core ARMv6, 512 MB RAM)\*\* unter Raspberry Pi OS / Debian Trixie – im Zusammenspiel mit Windows- und Arch-Linux-Clients.



> \*\*Architektur-Fokus (Resource Efficiency):\*\* Bewusstes Arbeiten auf stark begrenzter Hardware (512 MB RAM) ohne schwere Container- oder Drittanbieter-Frameworks – stattdessen Einsatz schlanker nativer Dienste (`Nginx`, `Systemd`, `UFW`, `Fail2ban`) und Python-Skripte auf Basis der Standardbibliothek.



\## Architektur \& Komponenten



\- \*\*Server-Plattform:\*\* Raspberry Pi 1B+ (512 MB RAM, Debian/Raspberry Pi OS) mit statischer Netzwerkkonfiguration (`nmcli`) und Stratum-2 NTP-Zeitsynchronisation

\- \*\*Storage-Management:\*\* 1-TB-Festplatte (`ext4`) per UUID und `x-systemd.automount` inkl. Samba-Dateifreigabe (`SMB`)

\- \*\*Security \& Hardening:\*\*

&#x20; - SSH-Absicherung (ausschließlich Ed25519-Key-Authentifizierung, kein Root-Login)

&#x20; - Host-Firewall (`UFW`) \& Intrusion Prevention (`Fail2ban`)

&#x20; - Gehärteter `Nginx`-Webserver (HTTP-to-HTTPS-Redirect, HTTP Basic Auth, Security-Header)

&#x20; - Eigene \*\*Internal Root CA (PKI)\*\* mit SAN-Zertifikaten

&#x20; - Umsetzung des \*Principle of Least Privilege\* über dedizierte System-User (`pimonitor`) und restriktive `/etc/sudoers.d/`-Regeln

\- \*\*Patch-Management \& Log-Rotation:\*\* Automatisierte Sicherheitsupdates via `unattended-upgrades`, `journald`-Speicherlimits (`100M`) und `logrotate`



\## Projektstruktur



\- `pi-scripts/pi\_monitor.py` – Ressourcenschonendes Python-Skript (Standardbibliothek) zur Überwachung von CPU-Temperatur, RAM, Festplatten, Systemd-Diensten und Fail2ban-Status mit HTML-Dashboard-Generierung

\- `pi-scripts/system-backup.sh` – Automatisiertes, AES-256-verschlüsseltes Konfigurations-Backup (`OpenSSL` + `PBKDF2`) inkl. Retention-Policy (14 Tage)

\- `windows-tools/pi\_watchdog.py` – Externes Netzwerk-Monitoring unter Windows (TCP-Port-Handshakes, Latenzmessung, HTTPS-Statusprüfung \& Desktop-Alerting)

\- `windows-tools/remote\_control.py` – Interaktives Python-CLI-Werkzeug zur Remote-Administration per SSH (Statusabfragen, Updates, sicheres Unmounten des Storage)



\## Disaster Recovery \& Audits



\- Regelmäßige Wiederherstellungstests (\*Restore-Tests\*) aus den verschlüsselten Backup-Archiven

\- Interne Security-Audits der Angriffsfläche mittels `nmap`, `ssh-audit` und `nikto`



