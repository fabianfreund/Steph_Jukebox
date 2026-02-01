from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
# Fix for the ImportError: safe_join is moved here in newer Flask/Werkzeug versions
from werkzeug.security import safe_join

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'music'
UNITY_FOLDER = 'webgl_build'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the music directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created folder: {UPLOAD_FOLDER}")

# --- ROUTES ---

# 1. Serve the Unity Game (Homepage)
@app.route('/')
def index():
    if not os.path.exists(os.path.join(UNITY_FOLDER, 'index.html')):
        return "<h1>Unity Build Not Found</h1><p>Ensure your WebGL files are in the 'webgl_build' folder.</p>"
    return send_from_directory(UNITY_FOLDER, 'index.html')

# 2. Support Unity static files (.js, .wasm, .data)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(UNITY_FOLDER, path)

# 3. API: List all songs for Unity
@app.route('/api/songs')
def list_songs():
    songs = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.mp3')]
    return jsonify(songs)

# 4. Stream Audio File
@app.route('/music/<path:filename>')
def get_music(filename):
    # safe_join prevents directory traversal attacks
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 5. Drag & Drop Upload Page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file and file.filename.endswith('.mp3'):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"✅ Successfully uploaded: {filename}")
            return jsonify({"status": "success", "file": filename})
        return jsonify({"error": "Invalid file type. Only MP3 allowed."}), 400
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jukebox Upload</title>
        <style>
            body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #f0f0f0; }
            #drop-zone { width: 400px; height: 250px; border: 4px dashed #007bff; border-radius: 20px;
                        display: flex; align-items: center; justify-content: center; background: white;
                        color: #007bff; font-weight: bold; transition: 0.3s; cursor: pointer; }
            #drop-zone.hover { background: #007bff; color: white; transform: scale(1.05); }
        </style>
    </head>
    <body>
        <h1>🎵 Jukebox Music Upload</h1>
        <div id="drop-zone">DRAG & DROP MP3 HERE</div>
        <p>Or click to select a file</p>
        <input type="file" id="file-input" style="display:none" accept=".mp3">
        <script>
            const zone = document.getElementById('drop-zone');
            const input = document.getElementById('file-input');

            zone.onclick = () => input.click();
            zone.ondragover = (e) => { e.preventDefault(); zone.classList.add('hover'); };
            zone.ondragleave = () => zone.classList.remove('hover');
            zone.ondrop = (e) => {
                e.preventDefault();
                zone.classList.remove('hover');
                handleFiles(e.dataTransfer.files);
            };
            input.onchange = (e) => handleFiles(e.target.files);

            function handleFiles(files) {
                for (let file of files) {
                    let formData = new FormData();
                    formData.append('file', file);
                    zone.innerText = "Uploading: " + file.name;
                    fetch('/upload', { method: 'POST', body: formData })
                    .then(res => res.json())
                    .then(data => {
                        alert('Uploaded: ' + data.file);
                        zone.innerText = "DRAG & DROP MP3 HERE";
                    })
                    .catch(err => alert('Upload failed'));
                }
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # Using 5001 for Mac compatibility (AirPlay blocks 5000)
    print("\n🚀 Jukebox Server active!")
    print("👉 Game: http://localhost:5001")
    print("👉 Upload: http://localhost:5001/upload\n")
    app.run(host='0.0.0.0', port=5001, debug=False)