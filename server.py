from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import subprocess
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join

app = Flask(__name__)
CORS(app)

# Configuration - Data folder OUTSIDE of git repository
# Use absolute path to avoid path resolution issues
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'jukebox_data'))
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'music')
COVERS_FOLDER = os.path.join(DATA_FOLDER, 'covers')
METADATA_FILE = os.path.join(DATA_FOLDER, 'songs_metadata.json')

UNITY_FOLDER = 'webgl_build'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COVERS_FOLDER'] = COVERS_FOLDER

# Ensure all directories exist
for folder in [DATA_FOLDER, UPLOAD_FOLDER, COVERS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created folder: {folder}")

# --- METADATA FUNCTIONS ---

def load_metadata():
    """Load metadata from JSON file"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_metadata(metadata):
    """Save metadata to JSON file"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def generate_song_id():
    """Generate a unique song ID"""
    return str(uuid.uuid4())

def get_song_by_id(song_id):
    """Get song data by ID"""
    metadata = load_metadata()
    for sid, data in metadata.items():
        if sid == song_id:
            return data
    return None

def get_all_songs():
    """Get all songs with their IDs"""
    metadata = load_metadata()
    songs = []
    for song_id, data in metadata.items():
        songs.append({
            'id': song_id,
            'filename': data.get('filename', ''),
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'cover': data.get('cover', None),
            'uploaded_at': data.get('uploaded_at', '')
        })
    return songs

# --- GIT FUNCTIONS ---

def get_git_info():
    """Get current git branch and last commit info"""
    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                        cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
        commit = subprocess.check_output(['git', 'log', '-1', '--format=%h - %s (%ar)'], 
                                        cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
        return {'branch': branch, 'commit': commit, 'available': True}
    except:
        return {'branch': 'N/A', 'commit': 'Git not available', 'available': False}

def git_pull():
    """Pull latest changes from git"""
    try:
        result = subprocess.check_output(['git', 'pull'], 
                                        cwd=os.path.dirname(os.path.abspath(__file__)),
                                        stderr=subprocess.STDOUT).decode()
        return {'success': True, 'output': result}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'output': e.output.decode()}

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
    # Don't serve our management routes as static files
    if path.startswith('api/') or path in ['upload', 'manage', 'settings']:
        return "Not found", 404
    return send_from_directory(UNITY_FOLDER, path)

# 3. API: List all songs with metadata for Unity
@app.route('/api/songs')
def list_songs():
    songs = get_all_songs()
    return jsonify(songs)

# 4. Stream Audio File by ID
@app.route('/api/stream/<song_id>')
def stream_song(song_id):
    print(f"\n{'='*60}")
    print(f"🎵 Stream request for ID: {song_id}")
    print(f"{'='*60}")
    
    # Load metadata
    metadata = load_metadata()
    print(f"📋 Available song IDs: {list(metadata.keys())}")
    
    # Get song data
    song = get_song_by_id(song_id)
    if not song:
        print(f"❌ Song not found for ID: {song_id}")
        return jsonify({"error": "Song not found"}), 404
    
    filename = song.get('filename')
    if not filename:
        print(f"❌ No filename in song data for ID: {song_id}")
        return jsonify({"error": "Invalid song data"}), 404
    
    print(f"📂 Filename from metadata: {filename}")
    print(f"📂 Upload folder: {app.config['UPLOAD_FOLDER']}")
    
    # Build absolute path
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    abs_file_path = os.path.abspath(file_path)
    
    print(f"📂 Relative path: {file_path}")
    print(f"📂 Absolute path: {abs_file_path}")
    print(f"📂 File exists: {os.path.exists(abs_file_path)}")
    
    # List all files in directory for debugging
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        all_files = os.listdir(app.config['UPLOAD_FOLDER'])
        print(f"📂 All files in upload folder: {all_files}")
    else:
        print(f"❌ Upload folder does not exist: {app.config['UPLOAD_FOLDER']}")
    
    if not os.path.exists(abs_file_path):
        print(f"❌ File not found: {abs_file_path}")
        return jsonify({"error": "Audio file not found on disk"}), 404
    
    print(f"✅ Streaming: {filename}")
    print(f"{'='*60}\n")
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 5. Serve Cover Images
@app.route('/covers/<path:filename>')
def get_cover(filename):
    return send_from_directory(app.config['COVERS_FOLDER'], filename)

# 6. Drag & Drop Upload Page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "Keine Datei gefunden"}), 400
        file = request.files['file']
        if file and file.filename.endswith('.mp3'):
            filename = secure_filename(file.filename)
            
            # Generate unique ID for this song
            song_id = generate_song_id()
            
            # Build absolute path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            abs_file_path = os.path.abspath(file_path)
            
            print(f"\n{'='*60}")
            print(f"📤 Upload Request")
            print(f"{'='*60}")
            print(f"Original filename: {file.filename}")
            print(f"Secure filename: {filename}")
            print(f"Song ID: {song_id}")
            print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
            print(f"File path: {abs_file_path}")
            
            # Save file
            file.save(abs_file_path)
            print(f"✅ File saved successfully")
            print(f"File exists after save: {os.path.exists(abs_file_path)}")
            
            # Initialize metadata with ID
            metadata = load_metadata()
            metadata[song_id] = {
                'filename': filename,
                'title': os.path.splitext(filename)[0],
                'description': '',
                'cover': None,
                'uploaded_at': datetime.now().isoformat()
            }
            save_metadata(metadata)
            print(f"✅ Metadata saved")
            print(f"{'='*60}\n")
            
            return jsonify({"status": "success", "file": filename, "id": song_id})
        return jsonify({"error": "Ungültiger Dateityp. Nur MP3 erlaubt."}), 400
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Upload</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f5f5f5; padding: 40px 20px;
            }
            .container { max-width: 500px; margin: 0 auto; background: white; 
                        padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            h1 { font-size: 24px; margin-bottom: 30px; color: #333; font-weight: 600; }
            #drop-zone { 
                border: 2px dashed #ddd; border-radius: 8px; padding: 60px 20px;
                text-align: center; color: #999; cursor: pointer; transition: all 0.2s;
                background: #fafafa;
            }
            #drop-zone:hover, #drop-zone.hover { 
                border-color: #333; background: #f5f5f5; color: #333;
            }
            .info { text-align: center; color: #999; margin: 15px 0; font-size: 14px; }
            .nav { display: flex; gap: 10px; margin-top: 30px; }
            .btn { 
                flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px;
                text-align: center; text-decoration: none; color: #333; font-size: 14px;
                background: white; transition: all 0.2s;
            }
            .btn:hover { background: #f5f5f5; border-color: #333; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Upload Music</h1>
            <div id="drop-zone">Drop MP3 files here</div>
            <p class="info">or click to select</p>
            <input type="file" id="file-input" style="display:none" accept=".mp3" multiple>
            <div class="nav">
                <a href="/manage" class="btn">Manage</a>
                <a href="/settings" class="btn">Settings</a>
            </div>
        </div>
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
                        alert('✓ Uploaded: ' + data.file);
                        zone.innerText = "Drop MP3 files here";
                    })
                    .catch(err => {
                        alert('✗ Upload failed');
                        zone.innerText = "Drop MP3 files here";
                    });
                }
            }
        </script>
    </body>
    </html>
    '''

# 7. Management Page (View and Edit Songs)
@app.route('/manage')
def manage_songs():
    songs = get_all_songs()
    
    songs_html = ""
    for song in songs:
        cover_preview = ""
        if song.get('cover'):
            cover_preview = f'<img src="/covers/{song["cover"]}" style="max-width: 100px; max-height: 100px; border-radius: 6px; border: 1px solid #eee;">'
        else:
            cover_preview = '<div style="width: 100px; height: 100px; background: #f5f5f5; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #ccc; font-size: 12px; border: 1px solid #eee;">No image</div>'
        
        song_id = song['id']
        songs_html += f'''
        <div class="song-item" data-id="{song_id}">
            <div class="song-cover">
                <div id="cover-preview-{song_id}">{cover_preview}</div>
                <input type="file" id="cover-{song_id}" accept="image/*" style="display:none" onchange="uploadCover('{song_id}', this)">
                <button onclick="document.getElementById('cover-{song_id}').click()" class="btn btn-small">Change image</button>
            </div>
            <div class="song-info">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" id="title-{song_id}" value="{song.get('title', '')}" class="form-input">
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="desc-{song_id}" class="form-input" rows="2">{song.get('description', '')}</textarea>
                </div>
                <div class="form-group">
                    <label>Filename</label>
                    <span class="filename">{song.get('filename', '')}</span>
                </div>
                <button onclick="saveSong('{song_id}')" class="btn btn-save">Save</button>
                <button onclick="deleteSong('{song_id}')" class="btn btn-delete">Delete</button>
            </div>
        </div>
        '''
    
    if not songs_html:
        songs_html = '<div style="background: white; padding: 40px; border-radius: 8px; text-align: center; color: #999;">No songs yet. <a href="/upload" style="color: #333;">Upload some!</a></div>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Manage Songs</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                   background: #f5f5f5; padding: 20px; }}
            .header {{ background: white; padding: 20px 30px; border-radius: 8px; 
                      margin-bottom: 20px; display: flex; justify-content: space-between; 
                      align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header h1 {{ font-size: 24px; color: #333; font-weight: 600; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .song-item {{ background: white; padding: 25px; border-radius: 8px; 
                         margin-bottom: 15px; display: grid; grid-template-columns: 120px 1fr; 
                         gap: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .song-cover {{ text-align: center; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; color: #666; font-size: 13px; 
                                margin-bottom: 6px; font-weight: 500; }}
            .form-input {{ width: 100%; padding: 10px; border: 1px solid #ddd; 
                          border-radius: 6px; font-size: 14px; }}
            .form-input:focus {{ outline: none; border-color: #333; }}
            .filename {{ color: #999; font-size: 13px; }}
            .btn {{ padding: 10px 20px; border: 1px solid #ddd; border-radius: 6px;
                   cursor: pointer; font-size: 14px; text-decoration: none; background: white;
                   color: #333; display: inline-block; transition: all 0.2s; }}
            .btn:hover {{ background: #f5f5f5; border-color: #333; }}
            .btn-small {{ padding: 8px 14px; font-size: 13px; margin-top: 8px; }}
            .btn-save {{ background: #333; color: white; border-color: #333; margin-right: 8px; }}
            .btn-save:hover {{ background: #000; }}
            .btn-delete {{ background: white; color: #d32f2f; border-color: #d32f2f; }}
            .btn-delete:hover {{ background: #d32f2f; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Manage Songs</h1>
                <div>
                    <a href="/upload" class="btn">Upload</a>
                    <a href="/settings" class="btn">Settings</a>
                    <a href="/" class="btn">Jukebox</a>
                </div>
            </div>
            
            {songs_html}
        </div>
        
        <script>
            function saveSong(songId) {{
                const title = document.getElementById('title-' + songId).value;
                const description = document.getElementById('desc-' + songId).value;
                
                fetch('/api/update-song', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ id: songId, title: title, description: description }})
                }})
                .then(res => res.json())
                .then(data => alert('✓ Saved'))
                .catch(err => alert('✗ Error'));
            }}
            
            function uploadCover(songId, input) {{
                if (!input.files || !input.files[0]) return;
                
                const formData = new FormData();
                formData.append('file', input.files[0]);
                formData.append('song_id', songId);
                
                fetch('/api/upload-cover', {{
                    method: 'POST',
                    body: formData
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.cover) {{
                        const preview = document.getElementById('cover-preview-' + songId);
                        preview.innerHTML = '<img src="/covers/' + data.cover + '?t=' + Date.now() + '" style="max-width: 100px; max-height: 100px; border-radius: 6px;">';
                        alert('✓ Cover uploaded');
                    }}
                }})
                .catch(err => alert('✗ Upload failed'));
            }}
            
            function deleteSong(songId) {{
                if (!confirm('Delete this song?')) return;
                
                fetch('/api/delete-song', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ id: songId }})
                }})
                .then(res => res.json())
                .then(data => {{ alert('✓ Deleted'); location.reload(); }})
                .catch(err => alert('✗ Error'));
            }}
        </script>
    </body>
    </html>
    '''

# 8. Settings Page
@app.route('/settings')
def settings_page():
    git_info = get_git_info()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Settings</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                   background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ background: white; padding: 20px 30px; border-radius: 8px; 
                      margin-bottom: 20px; display: flex; justify-content: space-between; 
                      align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header h1 {{ font-size: 24px; color: #333; font-weight: 600; }}
            .section {{ background: white; padding: 25px; border-radius: 8px; 
                       margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .section h2 {{ color: #333; margin-bottom: 18px; font-size: 16px; font-weight: 600; }}
            .info-row {{ display: flex; justify-content: space-between; padding: 10px 0;
                        border-bottom: 1px solid #f5f5f5; }}
            .info-row:last-child {{ border-bottom: none; }}
            .info-label {{ color: #666; font-size: 14px; }}
            .info-value {{ color: #333; font-family: 'SF Mono', Monaco, monospace; font-size: 13px; }}
            .btn {{ padding: 10px 20px; border: 1px solid #ddd; border-radius: 6px;
                   cursor: pointer; font-size: 14px; text-decoration: none; background: white;
                   color: #333; display: inline-block; transition: all 0.2s; }}
            .btn:hover {{ background: #f5f5f5; border-color: #333; }}
            .btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
            .btn-update {{ background: #333; color: white; border-color: #333; }}
            .btn-update:hover {{ background: #000; }}
            .btn-danger {{ background: white; color: #d32f2f; border-color: #d32f2f; }}
            .btn-danger:hover {{ background: #d32f2f; color: white; }}
            #output {{ background: #f5f5f5; color: #333; padding: 15px; border-radius: 6px;
                      font-family: 'SF Mono', Monaco, monospace; font-size: 12px; 
                      margin-top: 15px; max-height: 300px; overflow-y: auto; display: none;
                      border: 1px solid #e0e0e0; }}
            .status {{ display: inline-block; padding: 4px 10px; border-radius: 4px; 
                      font-size: 12px; font-weight: 500; }}
            .status-ok {{ background: #e8f5e9; color: #2e7d32; }}
            .status-error {{ background: #ffebee; color: #c62828; }}
            .note {{ color: #666; font-size: 13px; margin-top: 12px; line-height: 1.5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Settings</h1>
                <div>
                    <a href="/manage" class="btn">Manage</a>
                    <a href="/" class="btn">Jukebox</a>
                </div>
            </div>
            
            <div class="section">
                <h2>Data Storage</h2>
                <div class="info-row">
                    <span class="info-label">Music folder</span>
                    <span class="info-value">{UPLOAD_FOLDER}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Covers folder</span>
                    <span class="info-value">{COVERS_FOLDER}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Metadata file</span>
                    <span class="info-value">{METADATA_FILE}</span>
                </div>
                <p class="note">All data is stored outside the git repository and persists through updates.</p>
            </div>
            
            <div class="section">
                <h2>Git Version Control</h2>
                <div class="info-row">
                    <span class="info-label">Status</span>
                    <span class="status {'status-ok' if git_info['available'] else 'status-error'}">
                        {'Available' if git_info['available'] else 'Not available'}
                    </span>
                </div>
                <div class="info-row">
                    <span class="info-label">Branch</span>
                    <span class="info-value">{git_info['branch']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Last commit</span>
                    <span class="info-value">{git_info['commit']}</span>
                </div>
                
                <div style="margin-top: 18px;">
                    <button onclick="gitPull()" class="btn btn-update" {'disabled' if not git_info['available'] else ''}>
                        Update from Git
                    </button>
                    <button onclick="gitStatus()" class="btn" {'disabled' if not git_info['available'] else ''}>
                        Git Status
                    </button>
                </div>
                
                <div id="output"></div>
            </div>
        </div>
        
        <script>
            function showOutput(text) {{
                const output = document.getElementById('output');
                output.style.display = 'block';
                output.textContent = text;
            }}
            
            function gitPull() {{
                if (!confirm('Update app from Git? Server will restart.')) return;
                
                showOutput('Updating...');
                
                fetch('/api/git-pull', {{ method: 'POST' }})
                .then(res => res.json())
                .then(data => {{
                    showOutput(data.output);
                    if (data.success) {{
                        alert('✓ Update successful! Restarting...');
                        setTimeout(() => location.reload(), 3000);
                    }} else {{
                        alert('✗ Update failed. Check output.');
                    }}
                }})
                .catch(err => {{
                    showOutput('Error: ' + err);
                    alert('✗ Update error');
                }});
            }}
            
            function gitStatus() {{
                showOutput('Loading...');
                
                fetch('/api/git-status')
                .then(res => res.json())
                .then(data => showOutput(data.output))
                .catch(err => showOutput('Error: ' + err));
            }}
        </script>
    </body>
    </html>
    '''

# 9. API: Update song metadata
@app.route('/api/update-song', methods=['POST'])
def update_song():
    data = request.json
    song_id = data.get('id')
    title = data.get('title', '')
    description = data.get('description', '')
    
    if not song_id:
        return jsonify({"error": "Keine ID angegeben"}), 400
    
    metadata = load_metadata()
    if song_id not in metadata:
        return jsonify({"error": "Song nicht gefunden"}), 404
    
    metadata[song_id]['title'] = title
    metadata[song_id]['description'] = description
    save_metadata(metadata)
    
    return jsonify({"status": "success", "id": song_id})

# 10. API: Upload cover image
@app.route('/api/upload-cover', methods=['POST'])
def upload_cover():
    if 'file' not in request.files or 'song_id' not in request.form:
        return jsonify({"error": "Datei oder Song-ID fehlt"}), 400
    
    file = request.files['file']
    song_id = request.form['song_id']
    
    metadata = load_metadata()
    if song_id not in metadata:
        return jsonify({"error": "Song nicht gefunden"}), 404
    
    if file and file.filename:
        # Create a unique filename using song ID
        ext = os.path.splitext(file.filename)[1]
        cover_filename = secure_filename(f"{song_id}_cover{ext}")
        file.save(os.path.join(app.config['COVERS_FOLDER'], cover_filename))
        
        # Update metadata
        metadata[song_id]['cover'] = cover_filename
        save_metadata(metadata)
        
        return jsonify({"status": "success", "cover": cover_filename})
    
    return jsonify({"error": "Ungültige Datei"}), 400

# 11. API: Delete song
@app.route('/api/delete-song', methods=['POST'])
def delete_song():
    data = request.json
    song_id = data.get('id')
    
    if not song_id:
        return jsonify({"error": "Keine ID angegeben"}), 400
    
    metadata = load_metadata()
    if song_id not in metadata:
        return jsonify({"error": "Song nicht gefunden"}), 404
    
    song_data = metadata[song_id]
    
    # Delete MP3 file
    filename = song_data.get('filename')
    if filename:
        mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
    
    # Delete cover if exists
    if song_data.get('cover'):
        cover_path = os.path.join(app.config['COVERS_FOLDER'], song_data['cover'])
        if os.path.exists(cover_path):
            os.remove(cover_path)
    
    # Remove from metadata
    del metadata[song_id]
    save_metadata(metadata)
    
    return jsonify({"status": "success", "deleted": song_id})

# 12. API: Git pull
@app.route('/api/git-pull', methods=['POST'])
def api_git_pull():
    result = git_pull()
    return jsonify(result)

# 13. API: Git status
@app.route('/api/git-status')
def api_git_status():
    try:
        result = subprocess.check_output(['git', 'status'], 
                                        cwd=os.path.dirname(os.path.abspath(__file__))).decode()
        return jsonify({'output': result})
    except:
        return jsonify({'output': 'Git not available'}), 500

# 14. API: Reset metadata
@app.route('/api/reset-metadata', methods=['POST'])
def reset_metadata():
    save_metadata({})
    return jsonify({"status": "success"})

# 15. API: Debug - List files (only in debug mode)
@app.route('/api/debug/files')
def debug_files():
    """Debug endpoint to see what files actually exist"""
    try:
        return jsonify({
            "data_folder": DATA_FOLDER,
            "data_folder_exists": os.path.exists(DATA_FOLDER),
            "music_folder": UPLOAD_FOLDER,
            "music_folder_exists": os.path.exists(UPLOAD_FOLDER),
            "music_files": os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else [],
            "covers_folder": COVERS_FOLDER,
            "covers_folder_exists": os.path.exists(COVERS_FOLDER),
            "cover_files": os.listdir(COVERS_FOLDER) if os.path.exists(COVERS_FOLDER) else [],
            "metadata_file": METADATA_FILE,
            "metadata_exists": os.path.exists(METADATA_FILE),
            "metadata_content": load_metadata()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Jukebox Server aktiv!")
    print("="*60)
    print(f"👉 Jukebox:    http://localhost:5001")
    print(f"👉 Upload:     http://localhost:5001/upload")
    print(f"👉 Verwalten:  http://localhost:5001/manage")
    print(f"👉 Settings:   http://localhost:5001/settings")
    print("="*60)
    print(f"📂 Daten:      {DATA_FOLDER}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)