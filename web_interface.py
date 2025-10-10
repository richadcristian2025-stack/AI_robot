"""
web_interface.py - Voice Controlled Robot Web Interface
Integrates with AI command processing from stt_ai.py
Run: python web_interface.py
Access: http://localhost:4141
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import tempfile
import json
import time
import traceback
import io
import wave
from datetime import datetime
import numpy as np

# Import AI components from stt_ai.py
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

# ============================================================
# ROBOT CONTROLLER (from stt_ai.py)
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
            # Try auto-detect
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
        try:
            self.arduino = serial.Serial(port, self.baud_rate, timeout=2)
            time.sleep(2)
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
        if not command:
            return "EMPTY_COMMAND"
        if not self.connected:
            print(f"[SIMULATION] Command => {command}")
            return f"[SIMULASI] Perintah diterima: {command}"
        try:
            self.arduino.write((command + "\n").encode())
            time.sleep(0.05)
            resp = self.arduino.readline().decode(errors="ignore").strip()
            return resp if resp else "OK"
        except Exception as e:
            self.connected = False
            self.error = str(e)
            print("⚠️ Serial write/read error:", e)
            return "ERROR"

# ============================================================
# SPEECH-TO-TEXT (Whisper from Hugging Face)
# ============================================================
class SpeechToText:
    def __init__(self, model_name="openai/whisper-tiny"):
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
            print("❌ Failed to load Whisper model:", e)
            raise

    def _read_wav_from_bytes(self, wav_bytes: bytes):
        """Parse WAV bytes and return (numpy_array, sample_rate)"""
        try:
            bio = io.BytesIO(wav_bytes)
            wf = wave.open(bio, "rb")
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            sampwidth = wf.getsampwidth()
            
            if sampwidth == 2:
                dtype = np.int16
            elif sampwidth == 4:
                dtype = np.int32
            else:
                dtype = np.int16
            
            audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)
            
            # Normalize
            if dtype == np.int16:
                audio = audio / 32768.0
            elif dtype == np.int32:
                audio = audio / (2**31)
            
            # Convert stereo to mono
            if wf.getnchannels() == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
            
            return audio, sr
        except Exception:
            return None, None

    def process_audio(self, audio_bytes: bytes) -> str:
        """Process audio bytes and return transcribed text"""
        if not audio_bytes:
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
                    print("❌ Can't interpret audio bytes:", e)
                    return ""
            
            # Ensure 1D float32
            audio = audio.astype(np.float32)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)

            # Process with Whisper
            inputs = self.processor(audio, sampling_rate=sr, return_tensors="pt")
            input_features = inputs.input_features.to(self.device)
            
            predicted_ids = self.model.generate(input_features, max_new_tokens=512)
            text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
            
            print(f"🎙️ Transcribed: {text}")
            return text
        except Exception as e:
            print("❌ Error in process_audio:", e)
            traceback.print_exc()
            return ""

# ============================================================
# VOICE AI - Command Processing
# ============================================================
class VoiceAI:
    def __init__(self, use_intent_model: bool = True):
        self.use_intent_model = use_intent_model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load intent model (optional)
        self.intent_tokenizer = None
        self.intent_model = None
        
        if self.use_intent_model:
            try:
                intent_model_name = "microsoft/xtremedistil-l6-h256-uncased"
                print(f"🧠 Loading intent model ({intent_model_name}) on {self.device}...")
                self.intent_tokenizer = AutoTokenizer.from_pretrained(intent_model_name)
                self.intent_model = AutoModelForSequenceClassification.from_pretrained(intent_model_name).to(self.device)
                self.intent_model.eval()
                print("✅ Intent model loaded")
            except Exception as e:
                print("⚠️ Failed to load intent model, using keyword mapping only:", e)
                self.intent_tokenizer = None
                self.intent_model = None

        # Command mapping
        self.command_mapping = {
            "nyala": "L13:1:5",
            "hidup": "L13:1:5",
            "matikan": "L13:0:0",
            "mati": "L13:0:0",
            "suhu": "TR",
            "kelembaban": "HR",
            "maju": "MF:90:1",
            "mundur": "MB:90:1",
            "kiri": "ML:90:1",
            "kanan": "MR:90:1",
            "berhenti": "MS:0:0",
            "stop": "MS:0:0",
            "alarm": "S1000:1;S2000:1;S1000:1",
            "bel": "S2000:1",
        }

    def process_command(self, text: str) -> Optional[str]:
        """Process voice command and return Arduino command string"""
        if not text:
            return None
        
        txt = text.lower().strip()
        print(f"[AI] Processing: {txt}")
        
        # 1) Keyword matching first
        for keyword, cmd in self.command_mapping.items():
            if keyword in txt:
                print(f"[AI] Matched keyword: {keyword} -> {cmd}")
                return cmd
        
        # 2) Handle sound frequency commands
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
        
        # 3) Intent model fallback
        if self.intent_model and self.intent_tokenizer:
            try:
                inputs = self.intent_tokenizer(
                    txt,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=128
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.intent_model(**inputs)
                    probs = F.softmax(outputs.logits, dim=1)
                    cls = torch.argmax(probs, dim=1).item()
                    conf = probs[0][cls].item()
                
                label = str(cls)
                if hasattr(self.intent_model.config, 'id2label'):
                    label = self.intent_model.config.id2label.get(str(cls), str(cls))
                
                print(f"[AI] Intent model: {label} (conf: {conf:.2f})")
            except Exception as e:
                print(f"[AI] Intent model error: {e}")
        
        print("[AI] No command matched")
        return None

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize components
print("=" * 60)
print("🤖 Initializing Voice Controlled Robot System...")
print("=" * 60)

robot = RobotController(port="COM3", baud_rate=9600)
stt = SpeechToText(model_name="openai/whisper-tiny")
ai = VoiceAI(use_intent_model=True)

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
        # Step 1: Transcribe audio using Whisper
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
        
        # Step 2: Process command with AI
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
        if len(command_history) > 10:
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
    """Get the current status of the system"""
    return jsonify({
        "status": "ok",
        "is_connected": robot.connected,
        "port": robot.port,
        "last_command": last_result,
        "model": "whisper-tiny",
        "error": robot.error
    })

@app.route('/api/history')
def get_history():
    """Get command history"""
    return jsonify({
        "status": "ok",
        "history": command_history[-10:]
    })

@app.route('/api/check-connection')
def check_connection():
    """Check if Arduino is connected"""
    return jsonify({
        "connected": robot.connected,
        "port": robot.port,
        "message": f"Arduino connected on {robot.port}" if robot.connected else "Arduino not connected - Running in simulation mode",
        "error": robot.error
    })

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

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
    print(f"📡 Access the interface at: http://localhost:4141")
    print("="*60 + "\n")
    
    # Start the web server
    app.run(host='0.0.0.0', port=4141, debug=True, threaded=True)