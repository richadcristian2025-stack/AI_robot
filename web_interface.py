from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import tempfile
import json
import torch
import whisper
from datetime import datetime
import wave
import numpy as np

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize Whisper model
model = None

def load_model():
    """Load the Whisper model"""
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("tiny")
        print("Whisper model loaded successfully")
    return model

# Load model on startup
load_model()

# Global variable to store the last command result
last_result = {
    "status": "idle",
    "text": "",
    "command": "",
    "response": "",
    "timestamp": ""
}

# Command history
command_history = []

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/process_audio', methods=['POST'])
def process_audio():
    """Process audio data from the client"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name
        audio_file.save(audio_path)
    
    try:
        # Load the audio file
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # Make log-Mel spectrogram and move to the same device as model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
    
        # Detect the spoken language
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        
        # Decode the audio
        options = whisper.DecodingOptions(language=detected_lang, fp16=False)
        result = whisper.decode(model, mel, options)
        
        # Process the command (you can integrate with stt_ai.py here)
        global last_result
        last_result = {
            "status": "success",
            "text": result.text.strip(),
            "command": result.text.strip(),
            "response": f"Perintah diterima: {result.text.strip()}",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # Add to command history
        command_history.append(last_result.copy())
        if len(command_history) > 10:  # Keep only last 10 commands
            command_history.pop(0)
        
        return jsonify(last_result)
        
    except Exception as e:
        error_msg = f"Error processing audio: {str(e)}"
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500
    
    finally:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)

@app.route('/api/status')
def get_status():
    """Get the current status of the system"""
    return jsonify({
        "status": "ok",
        "is_connected": True,  # You can implement actual connection check
        "last_command": last_result,
        "model": "whisper-tiny"
    })

@app.route('/api/history')
def get_history():
    """Get command history"""
    return jsonify({
        "status": "ok",
        "history": command_history[-10:]  # Return last 10 commands
    })

def is_arduino_connected():
    """Check if Arduino is connected via serial port"""
    import serial.tools.list_ports
    
    # Common Arduino vendor and product IDs
    ARDUINO_IDS = {
        (0x2341, 0x0043),  # Arduino Uno
        (0x2341, 0x0001),  # Arduino Uno
        (0x2A03, 0x0043),  # Arduino Uno Clone
        (0x2341, 0x0010),  # Arduino Mega 2560
        (0x2A03, 0x0010),  # Arduino Mega 2560 Clone
        (0x2341, 0x8036),  # Arduino Leonardo
        (0x2341, 0x0036),  # Arduino Leonardo Bootloader
        (0x2A03, 0x8036),  # Arduino Leonardo Clone
    }
    
    # Check all available COM ports for Arduino
    for port in serial.tools.list_ports.comports():
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if (port.vid, port.pid) in ARDUINO_IDS:
                try:
                    # Try to open the port to verify it's actually an Arduino
                    ser = serial.Serial(port.device, 9600, timeout=1)
                    ser.close()
                    return True, port.device
                except (serial.SerialException, OSError):
                    continue
    return False, None

@app.route('/api/check-connection')
def check_connection():
    """Check if Arduino is connected"""
    is_connected, port = is_arduino_connected()
    
    if is_connected:
        return jsonify({
            "connected": True,
            "message": f"Arduino connected on {port}",
            "port": port
        })
    else:
        return jsonify({
            "connected": False,
            "message": "Arduino not found. Please check the connection.",
            "port": None
        })

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start the web server
    app.run(host='0.0.0.0', port=4141, debug=True)
