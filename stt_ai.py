"""
stt_ai.py - Voice Controlled Robot with Hugging Face Models
Mode:
  - Terminal: python stt_ai.py
  - Web:      python stt_ai.py --web  (serves on port 4141)
Notes:
  - Optional: set HF_TOKEN env var to login to Hugging Face (not required to run).
  - Expects Arduino on ARDUINO_PORT; will run in SIMULATION if not found.
"""

import argparse
import os
import io
import wave
import time
import traceback
import numpy as np
import serial
from typing import Optional

# Torch / HF
import torch
import torch.nn.functional as F
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from huggingface_hub import login

# Flask
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# ----------------------------
# Config
# ----------------------------
ARDUINO_PORT = "COM3"   # change if needed or set to None for auto-detect
BAUD_RATE = 9600
WEB_PORT = 4141

# Optional: HF token (set as env var HF_TOKEN) - not required to run locally
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN:
    try:
        login(token=HF_TOKEN)
        print("✅ Logged into Hugging Face Hub.")
    except Exception as e:
        print("⚠️ Hugging Face login failed or skipped:", e)

# ----------------------------
# Robot Controller
# ----------------------------
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
            self.connected = False
            self.error = "No port specified"

    def connect(self, port: str) -> bool:
        try:
            self.arduino = serial.Serial(port, self.baud_rate, timeout=2)
            time.sleep(2)  # allow Arduino to reset
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
            print(f"[SIM] Command => {command}")
            return "[SIMULASI] OK"
        try:
            # write and give Arduino a little time to respond
            self.arduino.write((command + "\n").encode())
            time.sleep(0.05)
            resp = self.arduino.readline().decode(errors="ignore").strip()
            return resp if resp else "OK"
        except Exception as e:
            self.connected = False
            self.error = str(e)
            print("⚠️ Serial write/read error:", e)
            return "ERROR"

# ----------------------------
# Speech-to-Text (Whisper Tiny)
# ----------------------------
class SpeechToText:
    def __init__(self, model_name="openai/whisper-tiny"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🧠 Loading Whisper model ({model_name}) on {self.device} ...")
        try:
            self.processor = WhisperProcessor.from_pretrained(model_name)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_name).to(self.device)
            # prevent forced tokens / weird prefixes
            try:
                self.model.config.forced_decoder_ids = None
            except Exception:
                pass
            print("✅ Whisper loaded.")
        except Exception as e:
            print("❌ Failed to load Whisper model:", e)
            raise

    def _read_wav_from_bytes(self, wav_bytes: bytes):
        """
        Try to parse WAV bytes (RIFF) using wave module; return (np_float32_array, sample_rate).
        """
        try:
            bio = io.BytesIO(wav_bytes)
            wf = wave.open(bio, "rb")
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            sampwidth = wf.getsampwidth()
            # interpret frames
            if sampwidth == 2:
                dtype = np.int16
            elif sampwidth == 4:
                dtype = np.int32
            else:
                dtype = np.int16
            audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)
            # normalize
            if dtype == np.int16:
                audio = audio / 32768.0
            elif dtype == np.int32:
                audio = audio / (2**31)
            # if stereo, convert to mono
            if wf.getnchannels() == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
            return audio, sr
        except Exception:
            return None, None

    def process_audio(self, audio_bytes: bytes) -> str:
        """
        Accepts raw bytes (preferably WAV) and returns transcribed text.
        If bytes are raw PCM int16, we will try to decode assuming 16kHz.
        """
        if not audio_bytes:
            return ""
        try:
            # Attempt to read as WAV
            audio, sr = self._read_wav_from_bytes(audio_bytes)
            if audio is None:
                # fallback: assume raw int16 PCM little-endian at 16000 Hz
                try:
                    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    sr = 16000
                except Exception as e:
                    print("❌ Can't interpret audio bytes:", e)
                    return ""
            # ensure 1D float32
            audio = audio.astype(np.float32)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)

            # Build processor input and transcribe
            inputs = self.processor(audio, sampling_rate=sr, return_tensors="pt")
            input_features = inputs.input_features.to(self.device)
            # generate
            predicted_ids = self.model.generate(input_features, max_new_tokens=512)
            text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
            print(f"🎙️ Transcribed: {text}")
            return text
        except Exception as e:
            print("❌ Error in process_audio:", e)
            traceback.print_exc()
            return ""

# ----------------------------
# Voice AI - simple keyword mapping + optional classifier fallback
# ----------------------------
class VoiceAI:
    def __init__(self, use_intent_model: bool = True):
        self.use_intent_model = use_intent_model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # load intent model (optional)
        self.intent_tokenizer = None
        self.intent_model = None
        if self.use_intent_model:
            try:
                intent_model_name = "microsoft/xtremedistil-l6-h256-uncased"
                print(f"🧠 Loading intent model ({intent_model_name}) on {self.device} ...")
                self.intent_tokenizer = AutoTokenizer.from_pretrained(intent_model_name)
                self.intent_model = AutoModelForSequenceClassification.from_pretrained(intent_model_name).to(self.device)
                self.intent_model.eval()
                print("✅ Intent model loaded.")
            except Exception as e:
                print("⚠️ Failed to load intent model, continuing with keyword mapping only:", e)
                self.intent_tokenizer = None
                self.intent_model = None

        # Simple command mapping by keywords -> exact commands for Arduino
        self.command_mapping = {
            "nyala": "L13:1:5",      # example: nyala -> LED pin13 ON 5s
            "hidup": "L13:1:5",
            "matikan": "L13:0:0",
            "suhu": "TR",
            "kelembaban": "HR",
            "maju": "MF:90:1",
            "mundur": "MB:90:1",
            "kiri": "ML:90:1",
            "kanan": "MR:90:1",
            "berhenti": "MS:0:0",
            "alarm": "S1000:1;S2000:1;S1000:1",
            "bel": "S2000:1",
            # Sound frequency patterns
            "nyalakan suara ": self._handle_sound_frequency,
            "bunyikan suara ": self._handle_sound_frequency,
            "mainkan suara ": self._handle_sound_frequency,
        }

    def _handle_sound_frequency(self, text: str) -> str:
        """Handle sound frequency commands like 'nyalakan suara 500 Hz'"""
        import re
        # Find all numbers in the text
        numbers = re.findall(r'\d+', text)
        if numbers:
            freq = int(numbers[0])
            # Limit frequency to valid range (20-20000 Hz)
            freq = max(20, min(20000, freq))
            duration = 2  # Default duration in seconds
            return f"S{freq}:{duration}"
        return ""

    def process_command(self, text: str) -> Optional[str]:
        """
        Process voice commands using AI model to determine the appropriate action.
        The AI will analyze the text and return the corresponding Arduino command.
        """
        if not text:
            return None
            
        txt = text.lower().strip()
        
        # Use the AI model to process the command
        if self.intent_model and self.intent_tokenizer:
            try:
                # Prepare the input for the AI model
                inputs = self.intent_tokenizer(
                    txt,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=128
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Get model predictions
                with torch.no_grad():
                    outputs = self.intent_model(**inputs)
                    probs = F.softmax(outputs.logits, dim=1)
                    cls = torch.argmax(probs, dim=1).item()
                    conf = probs[0][cls].item()
                
                # Get the predicted label
                label = self.intent_model.config.id2label.get(str(cls), str(cls))
                print(f"[AI] Predicted intent: {label} (confidence: {conf:.2f})")
                
                # Map intents to commands
                if 'light' in label.lower() or 'lampu' in label.lower():
                    if 'on' in label.lower() or 'nyala' in label.lower():
                        return "L13:1:5"  # Turn on LED for 5 seconds
                    elif 'off' in label.lower() or 'mati' in label.lower():
                        return "L13:0:0"  # Turn off LED
                
                # Handle sound commands
                elif 'sound' in label.lower() or 'suara' in label.lower():
                    # Extract frequency using regex
                    import re
                    numbers = re.findall(r'\d+', txt)
                    if numbers:
                        freq = int(numbers[0])
                        freq = max(20, min(20000, freq))  # Limit to valid range
                        return f"S{freq}:2"  # Play for 2 seconds
                    return "S1000:1"  # Default sound
                
                # Handle movement commands
                elif 'maju' in label.lower() or 'forward' in label.lower():
                    return "MF:90:1"
                elif 'mundur' in label.lower() or 'backward' in label.lower():
                    return "MB:90:1"
                elif 'kiri' in label.lower() or 'left' in label.lower():
                    return "ML:90:1"
                elif 'kanan' in label.lower() or 'right' in label.lower():
                    return "MR:90:1"
                elif 'berhenti' in label.lower() or 'stop' in label.lower():
                    return "MS:0:0"
                
                # Default action for unknown intents
                print(f"[AI] No specific action for intent: {label}")
                
            except Exception as e:
                print(f"[AI] Error processing command: {e}")
                return None
        
        # Fallback to simple keyword matching if AI model is not available
        print("[AI] Using fallback keyword matching")
        if any(word in txt for word in ["nyala", "hidup"]):
            return "L13:1:5"
        elif "mati" in txt or "matikan" in txt:
            return "L13:0:0"
        
        return None

        # 2) optional intent model fallback (we will just display predicted label)
        if self.intent_model and self.intent_tokenizer:
            try:
                inputs = self.intent_tokenizer(txt, return_tensors="pt", truncation=True, padding=True, max_length=128)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.intent_model(**inputs)
                    probs = F.softmax(outputs.logits, dim=1)
                    cls = torch.argmax(probs, dim=1).item()
                    conf = probs[0][cls].item()
                label = self.intent_model.config.id2label.get(str(cls), str(cls)) if isinstance(self.intent_model.config.id2label, dict) else self.intent_model.config.id2label.get(cls, str(cls)) if hasattr(self.intent_model.config, "id2label") else str(cls)
                print(f"[VoiceAI] Intent fallback -> label: {label} (conf {conf:.2f})")
                # Optionally map label -> command if you fine-tune model with specific labels
            except Exception as e:
                print("⚠️ Intent model inference failed:", e)

        return None

# ----------------------------
# Flask web app factory
# ----------------------------
def create_web_app(robot_controller: RobotController, stt: SpeechToText, ai: VoiceAI):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)

    @app.route("/")
    def index():
        return "🤖 Voice AI Web Interface - alive"

    @app.route("/check-connection", methods=["GET"])
    def check_connection():
        return jsonify({
            "connected": robot_controller.connected,
            "port": getattr(robot_controller, "port", None),
            "error": robot_controller.error,
        })

    @app.route("/process_audio", methods=["POST"])
    def process_audio():
        try:
            if "audio" not in request.files and "audio" not in request.files.keys():
                # try raw body
                audio_bytes = request.get_data()
            else:
                audio_file = request.files.get("audio")
                audio_bytes = audio_file.read() if audio_file else request.get_data()

            if not audio_bytes or len(audio_bytes) == 0:
                return jsonify({"error": "No audio data"}), 400

            # Transcribe
            text = stt.process_audio(audio_bytes)
            if not text:
                return jsonify({"text": "", "command": None, "response": "Tidak dapat mengenali suara"})

            # Process command
            cmd = ai.process_command(text)
            response = robot_controller.send_command(cmd) if cmd else "Perintah tidak dikenali"

            return jsonify({"text": text, "command": cmd, "response": response})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    return app

# ----------------------------
# Main entry
# ----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Run with web interface")
    parser.add_argument("--port", type=str, default=ARDUINO_PORT, help="Arduino COM port (e.g. COM3)")
    parser.add_argument("--no-intent-model", action="store_true", help="Disable loading intent classifier")
    args = parser.parse_args()

    # Robot controller
    rc = RobotController(args.port, BAUD_RATE)

    # Load STT
    try:
        stt = SpeechToText(model_name="openai/whisper-tiny")
    except Exception as e:
        print("❌ Failed to initialize STT model. Exiting.")
        return

    # Voice AI (keywords + optional intent model)
    ai = VoiceAI(use_intent_model=not args.no_intent_model)

    if args.web:
        app = create_web_app(rc, stt, ai)
        print(f"🌐 Running web server on http://0.0.0.0:{WEB_PORT}")
        app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)
    else:
        print("\n🎤 Terminal mode: ketik 'exit' untuk keluar.")
        while True:
            try:
                txt = input("Ketik perintah: ").strip()
                if not txt:
                    continue
                if txt.lower() in ("exit", "quit"):
                    break
                cmd = ai.process_command(txt)
                resp = rc.send_command(cmd) if cmd else "Perintah tidak dikenali"
                print(">>", resp)
            except KeyboardInterrupt:
                print("\nStopped.")
                break
            except Exception as e:
                print("Error:", e)

    # cleanup serial
    if rc.connected and rc.arduino:
        try:
            rc.arduino.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
