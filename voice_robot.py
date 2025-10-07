import whisper
import sounddevice as sd
import numpy as np
import tempfile
import wavio

# ==========================================================
# CONFIG
# ==========================================================
SAMPLE_RATE = 16000   # sample rate disarankan whisper
MODEL_NAME = "tiny"   # tiny, base, small, medium, large

# ==========================================================
# LOAD MODEL
# ==========================================================
print("🧠 Memuat model Whisper...")
model = whisper.load_model(MODEL_NAME)
print(f"✅ Model '{MODEL_NAME}' siap digunakan!\n")

# ==========================================================
# RECORD AUDIO
# ==========================================================
def record_audio(duration=5, samplerate=SAMPLE_RATE):
    print("🎤 Bicara sekarang...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    print("✅ Selesai merekam.")
    return np.squeeze(audio)

# ==========================================================
# RECOGNIZE SPEECH
# ==========================================================
def recognize_speech(audio_data, samplerate=SAMPLE_RATE):
    print("🔊 Memproses suara...")

    # Simpan sementara ke file WAV karena whisper memerlukan file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
        # Simpan audio float32 → 16-bit PCM WAV
        wavio.write(temp_file.name, audio_data, samplerate, sampwidth=2)

        # Transkripsi pakai Whisper
        result = model.transcribe(temp_file.name, fp16=False, language="indonesian")

    print("🗣️  Kamu bilang:", result["text"].strip())

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    audio = record_audio(duration=5)
    recognize_speech(audio)
