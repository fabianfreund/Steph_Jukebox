# 🎵 Unity Raspberry Pi Jukebox

Dieses Projekt ist eine interaktive 3D-Jukebox, die mit Unity entwickelt wurde. Sie läuft als WebGL-Anwendung auf einem Raspberry Pi (oder Mac/PC) und nutzt ein Python-Backend (Flask), um Musik flexibel zu verwalten, hochzuladen und zu streamen.

## 🚀 Features

- **Dynamisches Streaming**: Musik wird nicht in Unity fest verbaut, sondern live vom Server geladen
- **Drag-and-Drop Upload**: Lade neue Lieder einfach per Browser von deinem Laptop oder Smartphone hoch
- **Leichtgewichtig**: Native WebGL-Performance, optimiert für Raspberry Pi Hardware
- **Cross-Platform**: Läuft auf jedem Gerät mit einem modernen Browser

## 🛠 Installation und Einrichtung

### 1. Repository herunterladen

Öffne dein Terminal und klone das Projekt von GitHub:

```bash
git clone https://github.com/fabianfreund/Steph_Jukebox.git
cd Steph_Jukebox
```

### 2. Abhängigkeiten installieren

Du benötigst Python 3 sowie die Pakete Flask und Flask-CORS.

**Auf dem Mac:**
```bash
pip3 install flask flask-cors
```

**Auf dem Raspberry Pi:**
```bash
sudo apt-get update
sudo apt-get install python3-flask python3-flask-cors
```

### 3. Unity WebGL Build bereitstellen

Stelle sicher, dass deine exportierten WebGL-Dateien aus Unity im Ordner `webgl_build` liegen. Die Struktur sollte so aussehen:

```
Steph_Jukebox/
├── webgl_build/
│   ├── index.html
│   └── Build/
├── music/
└── server.py
```

## 🏃‍♂️ Starten der Jukebox

### 1. Server starten

Führe den Python-Server im Terminal aus:

```bash
python3 server.py
```

> **Hinweis:** Der Server startet standardmäßig auf Port 5001, um Konflikte auf dem Mac zu vermeiden.

### 2. Jukebox öffnen

Besuche im Browser:
```
http://localhost:5001
```

### 3. Musik hochladen

Besuche im Browser:
```
http://localhost:5001/upload
```

Hier kannst du MP3-Dateien einfach per Drag-and-Drop in das Fenster ziehen. Sie erscheinen sofort im `music` Ordner.

## 📂 Funktionsweise und Architektur

- **server.py**: Ein Flask-Webserver, der sowohl die Unity-App ausliefert als auch die API für die Musik bereitstellt
- **music**: Der Speicherort für alle hochgeladenen MP3-Dateien
- **webgl_build**: Enthält die kompilierte Unity WebGL-Anwendung

### Der Datenfluss:

1. Beim Start sendet Unity eine Anfrage an `http://localhost:5001/api/songs`
2. Der Server scannt den `music` Ordner und antwortet mit einer JSON-Liste (z. B. `["SongA.mp3", "SongB.mp3"]`)
3. Unity generiert basierend auf dieser Liste die Buttons in der UI
4. Beim Klick auf einen Button streamt Unity das Audio über `UnityWebRequestMultimedia` direkt vom Server

## 💡 Tipps für den Raspberry Pi

### Autostart im Kiosk-Modus

Damit die Jukebox beim Booten des Pi sofort im Vollbild startet, bearbeite die Autostart-Datei:

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Füge diese Zeilen am Ende hinzu:

```bash
@/usr/bin/python3 /home/pi/Steph_Jukebox/server.py
@chromium-browser --kiosk http://localhost:5001
```

### Unity Performance-Tipp

Für die beste Performance auf dem Pi:
- Deaktiviere in Unity unter **Project Settings > Player > Publishing Settings** die Option **Compression Format** (auf `Disabled` setzen)

