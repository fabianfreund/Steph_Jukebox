# 🎵 Steph's Jukebox

Unity WebGL Jukebox - Ready-to-go Installation für Raspberry Pi

## 📋 Voraussetzungen

- Raspberry Pi 3 oder 4 (4GB+ RAM empfohlen)
- Raspbian/Raspberry Pi OS installiert
- Internetverbindung
- Tastatur & Maus für Setup

## 🚀 Installation (3 einfache Schritte)

### Schritt 1: System vorbereiten

Öffne das Terminal und führe aus:

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git python3-flask python3-flask-cors -y
```

### Schritt 2: Jukebox installieren

```bash
cd ~
git clone https://github.com/fabianfreund/Steph_Jukebox.git
cd Steph_Jukebox
```

### Schritt 3: Server testen

```bash
python3 server.py
```

Öffne Browser: `http://localhost:5001`

Wenn die Jukebox läuft, drücke `Ctrl+C` um zu stoppen.

**Das war's - die Jukebox läuft!** 🎉

## 🔄 Autostart einrichten

### Automatischer Server-Start

```bash
sudo nano /etc/systemd/system/jukebox.service
```

Füge ein (mit `Ctrl+Shift+V` einfügen):

```ini
[Unit]
Description=Steph's Jukebox Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Steph_Jukebox
ExecStart=/usr/bin/python3 /home/pi/Steph_Jukebox/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Speichern: `Ctrl+O`, `Enter`, `Ctrl+X`

Service aktivieren:

```bash
sudo systemctl enable jukebox.service
sudo systemctl start jukebox.service
```

### Automatischer Browser-Start (Fullscreen)

```bash
mkdir -p ~/.config/lxsession/LXDE-pi
nano ~/.config/lxsession/LXDE-pi/autostart
```

Füge hinzu:

```bash
@chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:5001
@xset s off
@xset -dpms
@xset s noblank
```

Speichern: `Ctrl+O`, `Enter`, `Ctrl+X`

### Pi neustarten

```bash
sudo reboot
```

Nach dem Neustart startet Steph's Jukebox automatisch im Vollbild! 🎵

## 📂 Songs hochladen

### Option 1: Über Web-Interface

1. Öffne auf einem anderen Gerät im gleichen Netzwerk:
   ```
   http://raspberrypi.local:5001/upload
   ```
   
2. Ziehe MP3-Dateien in das Fenster

### Option 2: Direkt per USB

```bash
# USB-Stick einstecken, dann:
cp /media/pi/USB_STICK/*.mp3 ~/jukebox_data/music/
```

Danach über `/manage` Titel und Cover hinzufügen.

## 🔧 Nützliche Befehle

### Server-Status prüfen

```bash
sudo systemctl status jukebox.service
```

### Server neu starten

```bash
sudo systemctl restart jukebox.service
```

### Server-Logs ansehen

```bash
sudo journalctl -u jukebox.service -f
```

### Update installieren

```bash
cd ~/Steph_Jukebox
git pull
sudo systemctl restart jukebox.service
```

## 🌐 Von anderen Geräten zugreifen

Finde die IP-Adresse des Pi:

```bash
hostname -I
```

Dann auf anderen Geräten im Netzwerk:
```
http://192.168.1.XXX:5001
```

## 🐛 Häufige Probleme

### Problem: "Address already in use"

```bash
sudo lsof -ti:5001 | xargs sudo kill -9
sudo systemctl restart jukebox.service
```

### Problem: Browser startet nicht automatisch

Desktop-Umgebung aktivieren:

```bash
sudo raspi-config
# -> System Options -> Boot / Auto Login -> Desktop Autologin
```

### Problem: Jukebox lädt nicht

```bash
# Prüfe ob Server läuft:
curl http://localhost:5001

# Logs checken:
sudo journalctl -u jukebox.service -n 50
```

### Problem: Keine Songs sichtbar

```bash
# Prüfe Dateien:
ls -la ~/jukebox_data/music/

# Prüfe Metadaten:
cat ~/jukebox_data/songs_metadata.json
```

### Problem: Pi zu langsam

In `/boot/config.txt` hinzufügen:

```bash
sudo nano /boot/config.txt
```

Füge hinzu:
```
# GPU Memory
gpu_mem=256

# Overclock (nur Pi 4!)
over_voltage=6
arm_freq=2000
```

Dann:
```bash
sudo reboot
```

## 💾 Backup erstellen

```bash
# Auf USB-Stick sichern:
cp -r ~/jukebox_data /media/pi/USB_STICK/jukebox_backup_$(date +%Y%m%d)

# Oder als Archiv:
tar -czf ~/jukebox_backup.tar.gz ~/jukebox_data
```

## 🎯 Performance-Tipps

### Raspberry Pi optimieren:
```bash
# Swap erhöhen (wenn oft einfriert):
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Ändere: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Chromium beschleunigen:
# Verwende --disable-gpu im autostart wenn laggy
```

## 📊 Web-Interface

| Seite | URL | Funktion |
|-------|-----|----------|
| Jukebox | `/` | Unity WebGL App |
| Upload | `/upload` | MP3s hochladen |
| Manage | `/manage` | Titel/Cover bearbeiten |
| Settings | `/settings` | Git-Updates |

## 🔒 Ordnerstruktur

```
~/Steph_Jukebox/        # Git Repository
├── server.py           # Flask Server
├── webgl_build/        # Unity Build (aus Git)
├── .gitignore
└── README.md

~/jukebox_data/         # Deine Daten (sicher!)
├── music/              # MP3-Dateien
├── covers/             # Cover-Bilder
└── songs_metadata.json # Song-Infos
```

**Wichtig:** Der `jukebox_data` Ordner liegt außerhalb von Git.  
Bei Updates bleiben alle Songs erhalten!

## 📱 Remote-Zugriff einrichten (optional)

### Per Smartphone steuern:

```bash
sudo apt-get install avahi-daemon -y
sudo systemctl enable avahi-daemon
```

Dann von Smartphone:
```
http://raspberrypi.local:5001
```

## ❓ Support

Bei Problemen:

1. Logs prüfen: `sudo journalctl -u jukebox.service -f`
2. Debug-Endpoint: `http://localhost:5001/api/debug/files`
3. Issue auf GitHub öffnen

---

**Viel Spaß mit Steph's Jukebox! 🎵**

## 🔄 Autostart einrichten

### Automatischer Server-Start

```bash
sudo nano /etc/systemd/system/jukebox.service
```

Füge ein (mit `Ctrl+Shift+V` einfügen):

```ini
[Unit]
Description=Jukebox Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Steph_Jukebox
ExecStart=/usr/bin/python3 /home/pi/Steph_Jukebox/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Speichern: `Ctrl+O`, `Enter`, `Ctrl+X`

Service aktivieren:

```bash
sudo systemctl enable jukebox.service
sudo systemctl start jukebox.service
```

### Automatischer Browser-Start (Fullscreen)

```bash
mkdir -p ~/.config/lxsession/LXDE-pi
nano ~/.config/lxsession/LXDE-pi/autostart
```

Füge hinzu:

```bash
@chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:5001
@xset s off
@xset -dpms
@xset s noblank
```

Speichern: `Ctrl+O`, `Enter`, `Ctrl+X`

### Pi neustarten

```bash
sudo reboot
```

Nach dem Neustart sollte die Jukebox automatisch im Vollbild starten!

## 📂 Songs hochladen

### Option 1: Über Web-Interface

1. Öffne auf einem anderen Gerät im gleichen Netzwerk:
   ```
   http://raspberrypi.local:5001/upload
   ```
   
2. Ziehe MP3-Dateien in das Fenster

### Option 2: Direkt per USB

```bash
# USB-Stick einstecken, dann:
cp /media/pi/USB_STICK/*.mp3 ~/jukebox_data/music/
```

Danach über `/manage` Titel und Cover hinzufügen.

## 🔧 Nützliche Befehle

### Server-Status prüfen

```bash
sudo systemctl status jukebox.service
```

### Server neu starten

```bash
sudo systemctl restart jukebox.service
```

### Server-Logs ansehen

```bash
sudo journalctl -u jukebox.service -f
```

### Update installieren

```bash
cd ~/Steph_Jukebox
git pull
sudo systemctl restart jukebox.service
```

## 🌐 Von anderen Geräten zugreifen

Finde die IP-Adresse des Pi:

```bash
hostname -I
```

Dann auf anderen Geräten im Netzwerk:
```
http://192.168.1.XXX:5001
```

## 🐛 Häufige Probleme

### Problem: "Address already in use"

```bash
sudo lsof -ti:5001 | xargs sudo kill -9
sudo systemctl restart jukebox.service
```

### Problem: Browser startet nicht automatisch

Desktop-Umgebung aktivieren:

```bash
sudo raspi-config
# -> System Options -> Boot / Auto Login -> Desktop Autologin
```

### Problem: Jukebox lädt nicht

```bash
# Prüfe ob Server läuft:
curl http://localhost:5001

# Prüfe Unity-Build:
ls -la ~/Steph_Jukebox/webgl_build/

# Logs checken:
sudo journalctl -u jukebox.service -n 50
```

### Problem: Keine Songs sichtbar

```bash
# Prüfe Dateien:
ls -la ~/jukebox_data/music/

# Prüfe Metadaten:
cat ~/jukebox_data/songs_metadata.json
```

### Problem: Pi zu langsam

In `/boot/config.txt` hinzufügen:

```bash
sudo nano /boot/config.txt
```

Füge hinzu:
```
# GPU Memory
gpu_mem=256

# Overclock (nur Pi 4!)
over_voltage=6
arm_freq=2000
```

Dann:
```bash
sudo reboot
```

## 💾 Backup erstellen

```bash
# Auf USB-Stick sichern:
cp -r ~/jukebox_data /media/pi/USB_STICK/jukebox_backup_$(date +%Y%m%d)

# Oder als Archiv:
tar -czf ~/jukebox_backup.tar.gz ~/jukebox_data
```

## 🎯 Performance-Tipps

### Unity WebGL optimieren:
- Verwende **Disabled** Compression in Unity
- Reduziere Textur-Qualität auf 512px
- Verwende Mobile Shader Varianten
- Aktiviere **GPU Instancing**

### Raspberry Pi optimieren:
```bash
# Swap erhöhen (wenn oft einfriert):
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Ändere: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Chromium beschleunigen:
# Verwende --disable-gpu im autostart wenn laggy
```

## 📊 Web-Interface

| Seite | URL | Funktion |
|-------|-----|----------|
| Jukebox | `/` | Unity WebGL App |
| Upload | `/upload` | MP3s hochladen |
| Manage | `/manage` | Titel/Cover bearbeiten |
| Settings | `/settings` | Git-Updates |

## 🔒 Ordnerstruktur

```
~/Steph_Jukebox/        # Git Repository
├── server.py           # Flask Server
├── webgl_build/        # Unity Build
├── .gitignore
└── README.md

~/jukebox_data/         # Deine Daten (sicher!)
├── music/              # MP3-Dateien
├── covers/             # Cover-Bilder
└── songs_metadata.json # Song-Infos
```

**Wichtig:** Der `jukebox_data` Ordner liegt außerhalb von Git.  
Bei Updates bleiben alle Songs erhalten!

## 📱 Remote-Zugriff einrichten (optional)

### Per Smartphone steuern:

```bash
sudo apt-get install avahi-daemon -y
sudo systemctl enable avahi-daemon
```

Dann von Smartphone:
```
http://raspberrypi.local:5001
```

## ❓ Support

Bei Problemen:

1. Logs prüfen: `sudo journalctl -u jukebox.service -f`
2. Debug-Endpoint: `http://localhost:5001/api/debug/files`
3. Issue auf GitHub öffnen

---

**Viel Spaß mit deiner Jukebox! 🎵**

