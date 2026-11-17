\[Deutsch](README.md) | \[English](README.en.md)



\# PI-LAB Home-Lab Infrastructure \& Automation



This repository documents the setup, security hardening, monitoring, and automation of my local Linux server infrastructure running on a \*\*Raspberry Pi 1 Model B+ (700 MHz Single-Core ARMv6, 512 MB RAM)\*\* with Raspberry Pi OS / Debian Trixie, integrated with Windows and Arch Linux clients.



> \*\*Architecture Focus (Resource Efficiency):\*\* Deliberately engineered for constrained hardware (512 MB RAM) without heavy container runtimes or third-party bloat—relying instead on lightweight native services (`Nginx`, `Systemd`, `UFW`, `Fail2ban`) and Python scripts built purely on the standard library.



\## Architecture \& Components



\- \*\*Server Platform:\*\* Raspberry Pi 1B+ (512 MB RAM, Debian/Raspberry Pi OS) with static IP configuration (`nmcli`) and Stratum-2 NTP time synchronization

\- \*\*Storage Management:\*\* 1 TB external drive (`ext4`) mounted via UUID and `x-systemd.automount`, shared over the LAN via Samba (`SMB`)

\- \*\*Security \& Hardening:\*\*

&#x20; - SSH Hardening (Ed25519 key-only authentication, root login disabled)

&#x20; - Host Firewall (`UFW`) \& Intrusion Prevention (`Fail2ban`)

&#x20; - Hardened `Nginx` web server (HTTP-to-HTTPS redirect, HTTP Basic Auth, security headers)

&#x20; - Custom \*\*Internal Root CA (PKI)\*\* issuing SAN certificates

&#x20; - Enforcement of the \*Principle of Least Privilege\* using a dedicated system service user (`pimonitor`) and restricted `/etc/sudoers.d/` rules

\- \*\*Patch Management \& Log Rotation:\*\* Automated security updates via `unattended-upgrades`, `journald` disk usage caps (`100M`), and `logrotate`



\## Repository Structure



\- `pi-scripts/pi\_monitor.py` – Lightweight Python script (standard library only) monitoring CPU temperature, RAM, disk usage, systemd services, and Fail2ban status with live HTML dashboard generation

\- `pi-scripts/system-backup.sh` – Automated AES-256 encrypted configuration backup (`OpenSSL` + `PBKDF2`) with a 14-day retention policy

\- `windows-tools/pi\_watchdog.py` – External network watchdog for Windows (TCP port handshakes, latency measurement, HTTPS status checks, and native desktop alerts)

\- `windows-tools/remote\_control.py` – Interactive Python CLI tool for remote SSH administration (health checks, system updates, safe storage unmounting)



\## Disaster Recovery \& Security Audits



\- Regular restore verification tests from encrypted backup archives

\- Internal attack-surface and hardening audits using `nmap`, `ssh-audit`, and `nikto`



