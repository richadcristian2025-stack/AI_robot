"""
web_interface.py - Voice Controlled Robot Web Interface (FIXED)
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import time
import traceback
import io
import wave
from datetime import datetime
import numpy as np
import torch
import torch.nn.functional as F
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
import serial
import serial.tools.list_ports
from typing import Optional

# Import ML AI module
from ml_ai import MLRobotAI

# ============================================================
# CONFIGURATION
# ============================================================
class Config:
    # Serial settings
    SERIAL_PORT = os.getenv('SERIAL_PORT', 'COM3')  # Use env variable
    BAUD_RATE = 9600
    SERIAL_TIMEOUT = 2
    
    # Model settings
    WHISPER_MODEL = "openai/whisper-tiny"
    INTENT_MODEL = "microsoft/xtremedistil-l6-h256-uncased"
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = 4141
    DEBUG = True
    
    # Limits
    MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_HISTORY = 10

# ============================================================
# ROBOT CONTROLLER
# ============================================================
class RobotController:
    def __init__(self, port: Optional[str], baud_rate: int):
        self.port = port
        self.baud_rate = baud_rate
        self.arduino = None
        self.connected = False
        self.error = None
        
        if port:
            self.connect(port)
        else:
            detected_port = self._auto_detect_arduino()
            if detected_port:
                self.connect(detected_port)
            else:
                print("⚠️ Arduino not found. Running in SIMULATION mode.")

    def _auto_detect_arduino(self):
        """Auto-detect Arduino on available COM ports"""
        ARDUINO_IDS = {
            (0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043),
            (0x2341, 0x0010), (0x2A03, 0x0010), (0x2341, 0x8036),
            (0x2341, 0x0036), (0x2A03, 0x8036),
        }
        
        for port in serial.tools.list_ports.comports():
            if hasattr(port, 'vid') and hasattr(port, 'pid'):
                if (port.vid, port.pid) in ARDUINO_IDS:
                    print(f"🔍 Found Arduino on {port.device}")
                    return port.device
        return None

    def connect(self, port: str) -> bool:
        """Connect to Arduino"""
        try:
            self.arduino = serial.Serial(
                port, 
                self.baud_rate, 
                timeout=Config.SERIAL_TIMEOUT
            )
            time.sleep(2)  # Wait for Arduino to initialize
            self.connected = True
            self.port = port
            self.error = None
            print(f"✅ Connected to Arduino on {port}")
            return True
        except Exception as e:
            self.connected = False
            self.error = str(e)
            print(f"⚠️ Arduino connection failed: {self.error}")
            return False

    def send_command(self, command: str) -> str:
        """Send command to Arduino"""
        if not command:
            return "EMPTY_COMMAND"
        
        if not self.connected:
            print(f"[SIMULATION] Command => {command}")
            return f"[SIMULASI] Perintah diterima: {command}"
        
        try:
            self.arduino.write((command + "\n").encode())
            time.sleep(0.05)
            response = self.arduino.readline().decode(errors="ignore").strip()
            return response if response else "OK"
        except Exception as e:
            self.connected = False
            self.error = str(e)
            print(f"⚠️ Serial error: {e}")
            return "ERROR"

    def disconnect(self):
        """Disconnect from Arduino"""
        if self.arduino:
            try:
                self.arduino.close()
                self.connected = False
                print("✅ Arduino disconnected")
            except Exception as e:
                print(f"⚠️ Disconnect error: {e}")

# ============================================================
# SPEECH-TO-TEXT (Whisper)
# ============================================================
class SpeechToText:
    def __init__(self, model_name=None):
        model_name = model_name or Config.WHISPER_MODEL
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🧠 Loading Whisper model ({model_name}) on {self.device}...")
        
        try:
            self.processor = WhisperProcessor.from_pretrained(model_name)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_name).to(self.device)
            
            try:
                self.model.config.forced_decoder_ids = None
            except Exception:
                pass
            
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            raise

    def _read_wav_from_bytes(self, wav_bytes: bytes):
        """Parse WAV bytes and return (numpy_array, sample_rate)"""
        try:
            bio = io.BytesIO(wav_bytes)
            with wave.open(bio, "rb") as wf:
                sr = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                sampwidth = wf.getsampwidth()
                channels = wf.getnchannels()
            
            # Determine dtype
            dtype = np.int16 if sampwidth == 2 else (np.int32 if sampwidth == 4 else np.int16)
            
            # Convert to float32
            audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)
            
            # Normalize
            if dtype == np.int16:
                audio = audio / 32768.0
            elif dtype == np.int32:
                audio = audio / (2**31)
            
            # Convert stereo to mono
            if channels == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
            
            return audio, sr
        except Exception as e:
            print(f"⚠️ WAV parsing error: {e}")
            return None, None

    def process_audio(self, audio_bytes: bytes) -> str:
        """Process audio bytes and return transcribed text"""
        if not audio_bytes:
            return ""
        
        # Check size limit
        if len(audio_bytes) > Config.MAX_AUDIO_SIZE:
            print(f"⚠️ Audio too large: {len(audio_bytes)} bytes")
            return ""
        
        try:
            # Try to read as WAV
            audio, sr = self._read_wav_from_bytes(audio_bytes)
            
            if audio is None:
                # Fallback: assume raw PCM int16 at 16kHz
                try:
                    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    sr = 16000
                except Exception as e:
                    print(f"❌ Can't interpret audio bytes: {e}")
                    return ""
            
            # Ensure 1D float32
            audio = audio.astype(np.float32)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)

            # Process with Whisper
            inputs = self.processor(audio, sampling_rate=sr, return_tensors="pt")
            input_features = inputs.input_features.to(self.device)
            
            with torch.no_grad():
                predicted_ids = self.model.generate(input_features, max_new_tokens=512)
            
            text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
            
            print(f"🎙️ Transcribed: {text}")
            return text
            
        except Exception as e:
            print(f"❌ Error in process_audio: {e}")
            traceback.print_exc()
            return ""

# ============================================================
# VOICE AI - Command Processing using ML
# ============================================================
class VoiceAI:
    def __init__(self, use_ml_model: bool = True):
        self.use_ml_model = use_ml_model
        self.ml_ai = None
        
        if self.use_ml_model:
            try:
                print("🧠 Initializing ML AI model...")
                self.ml_ai = MLRobotAI()
                
                # Try to load existing model, otherwise train
                if not self.ml_ai.load_model('robot_ml_model.pkl'):
                    print("📚 Training new ML model...")
                    self.ml_ai.train(save_model=True)
                
                print("✅ ML AI model ready")
            except Exception as e:
                print(f"⚠️ ML model failed, using fallback: {e}")
                self.ml_ai = None
        
        # Fallback command mapping (if ML fails)
        self.command_mapping = {
            # Lights
            "nyala": "L13:1:5",
            "hidup": "L13:1:5",
            "light on": "L13:1:5",
            "turn on": "L13:1:5",
            "matikan": "L13:0:0",
            "mati": "L13:0:0",
            "padamkan": "L13:0:0",
            "light off": "L13:0:0",
            "turn off": "L13:0:0",
            
            # Sensors
            "suhu": "TR",
            "temperature": "TR",
            "kelembaban": "HR",
            "humidity": "HR",
            
            # Movement
            "maju": "MF:90:1",
            "forward": "MF:90:1",
            "mundur": "MB:90:1",
            "backward": "MB:90:1",
            "kiri": "ML:90:1",
            "left": "ML:90:1",
            "kanan": "MR:90:1",
            "right": "MR:90:1",
            
            # Control
            "berhenti": "MS:0:0",
            "stop": "MS:0:0",
            "diam": "MS:0:0",
            
            # Sound
            "alarm": "S1000:1;S2000:1;S1000:1",
            "sirine": "S1000:1;S2000:1;S1000:1",
            "bel": "S2000:1",
            "bunyi": "S2000:1",
        }

    def process_command(self, text: str) -> Optional[str]:
        """Process voice command and return Arduino command string"""
        if not text:
            return None
        
        txt = text.lower().strip()
        print(f"[AI] Processing: {txt}")
        
        # 1) Try ML model first
        if self.ml_ai:
            try:
                command = self.ml_ai.process_command(txt, threshold=0.3, verbose=True)
                if command:
                    print(f"[ML AI] Command found: {command}")
                    return command
            except Exception as e:
                print(f"[ML AI] Error: {e}")
        
        # 2) Fallback to keyword matching
        print("[AI] Using fallback keyword matching...")
        for keyword, cmd in self.command_mapping.items():
            if keyword in txt:
                print(f"[AI] Matched keyword: {keyword} -> {cmd}")
                return cmd
        
        # 3) Handle sound frequency commands
        import re
        if any(word in txt for word in ["suara", "nada", "bunyi", "frekuensi"]):
            numbers = re.findall(r'\d+', txt)
            if numbers:
                freq = int(numbers[0])
                freq = max(20, min(20000, freq))
                duration = 2
                cmd = f"S{freq}:{duration}"
                print(f"[AI] Sound frequency: {freq}Hz -> {cmd}")
                return cmd
        
        print("[AI] No command matched")
        return None

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={
    r"/api/*": {"origins": "*"},  # Allow all origins for API
    r"/static/*": {"origins": "*"}  # Allow all origins for static files
})

# Initialize components
print("=" * 60)
print("🤖 Initializing Voice Controlled Robot System...")
print("=" * 60)

robot = RobotController(port=Config.SERIAL_PORT, baud_rate=Config.BAUD_RATE)
stt = SpeechToText()
ai = VoiceAI(use_ml_model=True)  # Use ML model from ml_ai.py

# Global variables
last_result = {
    "status": "idle",
    "text": "",
    "command": "",
    "response": "",
    "timestamp": ""
}

command_history = []

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/process_audio', methods=['POST'])
def process_audio():
    """Process audio data from the client"""
    global last_result
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    audio_bytes = audio_file.read()
    
    if not audio_bytes:
        return jsonify({"error": "Empty audio file"}), 400
    
    try:
        # Step 1: Transcribe audio
        print("\n" + "="*50)
        print("🎤 Processing new audio...")
        text = stt.process_audio(audio_bytes)
        
        if not text:
            last_result = {
                "status": "error",
                "text": "",
                "command": "",
                "response": "Tidak dapat mengenali suara",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            return jsonify(last_result)
        
        # Step 2: Process command
        command = ai.process_command(text)
        
        # Step 3: Send to robot
        if command:
            response = robot.send_command(command)
            status = "success"
        else:
            response = "Perintah tidak dikenali"
            status = "error"
            command = ""
        
        # Step 4: Store result
        last_result = {
            "status": status,
            "text": text,
            "command": command,
            "response": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # Add to history
        command_history.append(last_result.copy())
        if len(command_history) > Config.MAX_HISTORY:
            command_history.pop(0)
        
        print(f"✅ Result: {last_result}")
        print("="*50 + "\n")
        
        return jsonify(last_result)
        
    except Exception as e:
        error_msg = f"Error processing audio: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": error_msg}), 500

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        "status": "ok",
        "is_connected": robot.connected,
        "port": robot.port,
        "last_command": last_result,
        "model": Config.WHISPER_MODEL,
        "error": robot.error
    })

@app.route('/api/history')
def get_history():
    """Get command history"""
    return jsonify({
        "status": "ok",
        "history": list(reversed(command_history[-Config.MAX_HISTORY:]))
    })

@app.route('/api/check-connection')
def check_connection():
    """Check Arduino connection"""
    return jsonify({
        "connected": robot.connected,
        "port": robot.port,
        "message": f"Arduino connected on {robot.port}" if robot.connected 
                  else "Arduino not connected - Running in simulation mode",
        "error": robot.error
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

# ============================================================
# CLEANUP
# ============================================================

def cleanup():
    """Cleanup resources on shutdown"""
    print("\n🛑 Shutting down...")
    robot.disconnect()
    print("✅ Cleanup complete")

import atexit
atexit.register(cleanup)

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("\n" + "="*60)
    print("🌐 Starting web server...")
    print(f"📡 Access: http://localhost:{Config.PORT}")
    print(f"🔌 Arduino: {'Connected' if robot.connected else 'Simulation Mode'}")
    print(f"🧠 Model: {Config.WHISPER_MODEL}")
    print("="*60 + "\n")
    
    # Start server
    try:
        app.run(
            host=Config.HOST, 
            port=Config.PORT, 
            debug=Config.DEBUG, 
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        cleanup()