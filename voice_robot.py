import whisper
import sounddevice as sd
import numpy as np

model = whisper.load_model("tiny")

def record_audio(duration=5, samplerate=16000):
    print("Bicara sekarang...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    print("Selesai merekam.")
    return np.squeeze(audio)

def recognize_speech(audio):
    print("Memproses suara...")
    result = model.transcribe(audio, fp16=False, language="indonesian")
    print("Kamu bilang:", result["text"])

if __name__ == "__main__":
    audio_data = record_audio(5)
    recognize_speech(audio_data)
