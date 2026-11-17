import subprocess
import os

PI_HOST = "admin@192.168.0.32"


def run_ssh_command(cmd: str, interactive: bool = False):
    """Fuehrt einen Befehl ueber den hinterlegten SSH-Key auf dem Pi aus."""
    print(f"\n>>> Fuehre auf PI-LAB aus: {cmd}\n" + "-" * 50)
    if interactive:
        subprocess.run(["ssh", "-t", PI_HOST, cmd])
    else:
        subprocess.run(["ssh", PI_HOST, cmd])
    print("-" * 50)
    input("\nDruecke Enter, um ins Menue zurueckzukehren...")


def main_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("==========================================")
        print("      PI-LAB REMOTE ADMIN CONTROL         ")
        print("==========================================")
        print(" [1] System-Status (Temperatur, RAM, Disk)")
        print(" [2] Security-Check (Fail2ban & Ports)")
        print(" [3] Live-Dashboard jetzt aktualisieren")
        print(" [4] 1TB-Festplatte sicher aushaengen (Nacht)")
        print(" [5] System-Updates einspielen (apt)")
        print(" [6] Interaktive SSH-Shell oeffnen")
        print(" [0] Beenden")
        print("==========================================")

        choice = input("Auswahl eingeben: ").strip()

        if choice == "1":
            run_ssh_command("uptime && free -h && df -h / /mnt/storage")
        elif choice == "2":
            run_ssh_command("sudo fail2ban-client status sshd && echo '' && sudo ss -tulpn")
        elif choice == "3":
            run_ssh_command("sudo /home/admin/scripts/pi_monitor.py")
        elif choice == "4":
            run_ssh_command("cd ~ && sudo systemctl restart smbd && sudo umount /mnt/storage && echo 'Platte sicher ausgehaengt!'")
        elif choice == "5":
            run_ssh_command("sudo apt update && sudo apt upgrade -y", interactive=True)
        elif choice == "6":
            subprocess.run(["ssh", PI_HOST])
        elif choice == "0":
            print("Auf Wiedersehen!")
            break
        else:
            input("Ungueltige Eingabe! Enter druecken...")


if __name__ == "__main__":
    main_menu()
