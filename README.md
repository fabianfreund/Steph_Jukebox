# 🎵 Unity Raspberry Pi Jukebox (Pro Edition)

Eine professionelle 3D-Jukebox mit **Song-IDs**, **externem Datenspeicher** und **Git-Update-Funktion**, entwickelt mit Unity und Flask.

## 🚀 Neue Features (Pro Edition)

### ✅ Sicherer Update-Prozess
- **Externer Datenspeicher**: Alle Uploads werden außerhalb des Git-Repos in `../jukebox_data/` gespeichert
- **Git-Updates**: Hole neue Versionen direkt vom Server ohne Datenverlust
- **Song-IDs**: Jeder Upload erhält eine eindeutige UUID, keine Dateinamen-Konflikte mehr

### 📝 Verwaltung
- Titel, Beschreibungen und Cover bearbeiten
- Songs über eindeutige IDs verwalten
- Upload-Zeitstempel für jeden Song

### ⚙️ Settings-Panel
- Git-Status anzeigen
- Updates mit einem Klick installieren
- Daten-Pfade einsehen
- Metadaten zurücksetzen

## 📁 Ordnerstruktur

```
Steph_Jukebox/                  # Git Repository
├── server.py                    # Flask Server
├── webgl_build/                 # Unity WebGL Build
│   ├── index.html
│   └── Build/
├── .gitignore                   # Schützt jukebox_data/
└── README.md

jukebox_data/                    # AUSSERHALB von Git (bleibt bei Updates erhalten!)
├── music/                       # MP3-Dateien
├── covers/                      # Cover-Bilder
└── songs_metadata.json          # Song-Metadaten mit IDs
```

## 🛠 Installation

### 1. Repository klonen

```bash
git clone https://github.com/fabianfreund/Steph_Jukebox.git
cd Steph_Jukebox
```

### 2. Abhängigkeiten installieren

**Mac:**
```bash
pip3 install flask flask-cors
```

**Raspberry Pi:**
```bash
sudo apt-get update
sudo apt-get install python3-flask python3-flask-cors
```

### 3. Unity WebGL Build

Exportiere deine Unity-App nach `webgl_build/`

## 🏃‍♂️ Server starten

```bash
python3 server.py
```

Der Server erstellt automatisch den `jukebox_data` Ordner beim ersten Start.

### Verfügbare Seiten:

| URL | Beschreibung |
|-----|--------------|
| `http://localhost:5001` | 🎮 **Jukebox** - Unity WebGL App |
| `http://localhost:5001/upload` | ➕ **Upload** - Neue Songs hochladen |
| `http://localhost:5001/manage` | 📝 **Verwaltung** - Songs bearbeiten |
| `http://localhost:5001/settings` | ⚙️ **Einstellungen** - Git-Updates & System |

## 🔄 Updates installieren

### Über die Web-UI (empfohlen):

1. Gehe zu `http://localhost:5001/settings`
2. Klicke auf "🔄 Update von Git holen"
3. Bestätige die Aktion
4. Warte bis der Server neu startet

### Manuell via Terminal:

```bash
cd Steph_Jukebox
git pull
python3 server.py
```

**Wichtig:** Deine Musik, Cover und Metadaten bleiben erhalten, da sie außerhalb des Git-Repos liegen!

## 📝 Song-IDs System

### Wie es funktioniert:

Jeder hochgeladene Song erhält eine eindeutige UUID:

```json
{
  "a1b2c3d4-e5f6-7890-abcd-ef1234567890": {
    "filename": "song.mp3",
    "title": "Mein Song",
    "description": "Artist - Album (2024)",
    "cover": "a1b2c3d4-e5f6-7890-abcd-ef1234567890_cover.jpg",
    "uploaded_at": "2024-02-01T10:30:00"
  }
}
```

### Vorteile:

- ✅ Dateinamen können sich ändern ohne Probleme
- ✅ Keine Konflikte bei gleichen Dateinamen
- ✅ Einfaches Tracking und Referenzieren
- ✅ Cover-Bilder verwenden Song-ID als Namen

## 🎮 Unity Integration

### API-Endpunkte für Unity:

```csharp
// Songs mit IDs laden
GET /api/songs
// Response: Array von Song-Objekten mit IDs

// Song streamen (über ID, nicht Dateiname!)
GET /api/stream/{song_id}

// Cover laden
GET /covers/{filename}
```

### Beispiel API-Response:

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "song.mp3",
    "title": "Awesome Song",
    "description": "Artist - Album",
    "cover": "a1b2c3d4_cover.jpg",
    "uploaded_at": "2024-02-01T10:30:00"
  }
]
```

### JukeboxManager.cs Setup:

1. Füge `JukeboxManager.cs` zu einem GameObject hinzu
2. Erstelle Button-Prefab für Songs
3. Verknüpfe UI-Elemente im Inspector:
   - `songButtonContainer`: Transform für Buttons
   - `songButtonPrefab`: Button-Prefab
   - `nowPlayingTitle`: Text für Titel
   - `nowPlayingDescription`: Text für Beschreibung
   - `nowPlayingCover`: Image für Cover

### Wichtiger Unterschied:

```csharp
// ALT (Dateiname-basiert):
string audioURL = $"{serverURL}/music/{song.filename}";

// NEU (ID-basiert):
string audioURL = $"{serverURL}/api/stream/{song.id}";
```

## ⚙️ Settings-Panel Features

### Git-Informationen:
- Aktueller Branch
- Letzter Commit
- Git-Status

### Update-Funktion:
- Automatisches `git pull`
- Server-Neustart nach Update
- Fehlermeldungen im Output-Fenster

### Wartung:
- Metadaten zurücksetzen (Songs bleiben erhalten)
- Pfade anzeigen

## 🔒 Datensicherheit

### Was ist in Git?
✅ Server-Code (`server.py`)  
✅ Unity-Build (`webgl_build/`)  
✅ README & Dokumentation  

### Was ist NICHT in Git?
❌ Hochgeladene Songs (`../jukebox_data/music/`)  
❌ Cover-Bilder (`../jukebox_data/covers/`)  
❌ Metadaten (`../jukebox_data/songs_metadata.json`)  

Die `.gitignore` Datei schützt automatisch den `jukebox_data` Ordner!

## 💾 Backup

Erstelle regelmäßig Backups deiner Daten:

```bash
# Komplettes Backup
tar -czf jukebox_backup_$(date +%Y%m%d).tar.gz ../jukebox_data/

# Nur Metadaten
cp ../jukebox_data/songs_metadata.json ~/backups/
```

## 🚀 Deployment auf Raspberry Pi

### Autostart einrichten:

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Füge hinzu:

```bash
@/usr/bin/python3 /home/pi/Steph_Jukebox/server.py
@chromium-browser --kiosk http://localhost:5001
```

### Systemd Service (empfohlen):

Erstelle `/etc/systemd/system/jukebox.service`:

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

Aktivieren:

```bash
sudo systemctl enable jukebox.service
sudo systemctl start jukebox.service
```

## 🔧 Troubleshooting

### Problem: Git-Update funktioniert nicht

**Lösung:**
```bash
cd Steph_Jukebox
git fetch origin
git reset --hard origin/main
python3 server.py
```

### Problem: Songs verschwunden nach Update

**Antwort:** Das sollte nicht passieren! Songs liegen außerhalb von Git.

**Prüfen:**
```bash
ls -la ../jukebox_data/music/
cat ../jukebox_data/songs_metadata.json
```

### Problem: "Permission denied" bei Git-Pull

**Lösung:**
```bash
cd Steph_Jukebox
sudo chown -R $USER:$USER .git
```

### Problem: Server startet nicht nach Update

**Lösung:**
```bash
# Dependencies neu installieren
pip3 install --upgrade flask flask-cors

# Server manuell starten
python3 server.py
```

## 📊 API-Referenz

### Songs abrufen
```
GET /api/songs
Response: Array von Song-Objekten
```

### Song streamen
```
GET /api/stream/{song_id}
Response: MP3-Datei
```

### Song aktualisieren
```
POST /api/update-song
Body: {"id": "...", "title": "...", "description": "..."}
```

### Cover hochladen
```
POST /api/upload-cover
Form Data: file, song_id
```

### Song löschen
```
POST /api/delete-song
Body: {"id": "..."}
```

### Git-Update
```
POST /api/git-pull
Response: {"success": true, "output": "..."}
```

## 🎯 Best Practices

### Für Entwickler:
1. ✅ Teste Updates zuerst lokal
2. ✅ Erstelle Backups vor großen Änderungen
3. ✅ Verwende Feature-Branches für neue Features
4. ✅ Dokumentiere Breaking Changes im README

### Für Benutzer:
1. ✅ Regelmäßige Backups von `jukebox_data/`
2. ✅ Prüfe Git-Status vor Updates
3. ✅ Verwende aussagekräftige Titel & Beschreibungen
4. ✅ Behalte originale Dateinamen bei

## 🛣 Roadmap

### Geplante Features:
- [ ] Playlist-System mit IDs
- [ ] Bulk-Upload mit Metadaten-Import
- [ ] Automatische Cover-Downloads (Spotify/iTunes API)
- [ ] Song-Statistiken (Play Count, Last Played)
- [ ] User-System mit Favoriten
- [ ] QR-Code für Mobile-Upload
- [ ] WebSocket für Live-Updates
- [ ] Datenbank-Migration (SQLite)

## 📝 Changelog

### v2.0.0 (Current)
- ✨ Song-IDs System (UUIDs)
- ✨ Externer Datenspeicher (`jukebox_data/`)
- ✨ Settings-Panel mit Git-Integration
- ✨ Upload-Zeitstempel
- 🔒 .gitignore für Datenschutz
- 📚 Erweiterte Dokumentation

### v1.0.0
- 🎵 Basis Jukebox-Funktionalität
- 📤 File Upload
- 🖼️ Cover-Bilder
- ✏️ Metadaten-Verwaltung

## 📧 Support

Bei Fragen oder Problemen:
- 🐛 Issue auf GitHub öffnen
- 📧 Email an [deine-email]
- 💬 Discord: [dein-discord]

## 📄 Lizenz

[MIT License]

---

**Entwickelt mit ❤️ von Fabian Freund**  
Powered by Unity, Flask & Raspberry Pi