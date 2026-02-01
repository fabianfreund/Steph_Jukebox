#!/bin/bash

echo "🚀 Starting Jukebox Setup..."

# 1. Update system and install Python dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-flask flask-cors

# 2. Create the music directory if it doesn't exist
if [ ! -d "music" ]; then
    mkdir music
    echo "📁 Created 'music' folder."
fi

# 3. Check if Unity build exists
if [ ! -d "webgl_build" ]; then
    echo "⚠️ Warning: 'webgl_build' folder not found. Please upload your Unity export."
fi

echo "✅ Setup Complete!"
echo "🎵 Starting the Jukebox Server on http://localhost:8080"

# 4. Start the server
python3 server.py