# 🤖 PANDUAN LENGKAP VOICE-CONTROLLED ROBOT

## 🌐 Web Interface (Port 4141)
Antarmuka web yang modern dan responsif di port 4141 dengan kontrol suara yang mudah digunakan.

### 🎨 Fitur Web:
- 🎤 Tombol mikrofon interaktif dengan efek visual
- 🎯 Tampilan real-time hasil konversi suara ke teks
- 🤖 Respons langsung dari robot dengan animasi
- 📱 Desain responsif yang mendukung perangkat mobile
- 🎨 Tema gelap/terang otomatis
- 📊 Indikator koneksi Arduino yang jelas
- 🔊 Efek suara untuk feedback interaksi

### Cara Mengakses:
1. Pastikan server berjalan
2. Buka browser
3. Kunjungi: http://localhost:4141
4. Klik tombol mikrofon dan mulai berbicara

## 📁 STRUKTUR PROJECT
```
├── robot.ino           # Kontrol hardware (Arduino)
├── voice_robot.py      # Input suara (Speech-to-Text)
├── stt_ai.py          # AI processing & kontrol
└── PANDUAN.md         # Panduan ini

## 🔧 INSTALASI LENGKAP

### 1. Instal Python (Jika Belum Ada)
- Download Python 3.8+ dari [python.org](https://www.python.org/downloads/)
- Pastikan centang "Add Python to PATH" saat instalasi

### 2. Install Library Python
Buka Command Prompt (Windows) atau Terminal (Mac/Linux), lalu jalankan perintah berikut:

```bash
# Update pip terlebih dahulu
python -m pip install --upgrade pip

# Dependensi utama untuk AI dan Pemrosesan Suara
pip install torch torchaudio transformers
pip install openai-whisper
pip install numpy scipy

# Library untuk Web Interface
pip install flask flask-cors pyserial

# Library untuk audio processing
pip install sounddevice wave soundfile

# Library tambahan
pip install python-dotenv

# Khusus Windows (jika diperlukan)
pip install pipwin
pipwin install pyaudio
```

> **Catatan:** Daftar library di atas akan diperbarui secara otomatis saat Anda menambahkan library baru menggunakan pip. Pastikan untuk selalu memperbarui PANDUAN.md setelah menginstall library baru.

### 3. Install Arduino IDE & Library
1. Download Arduino IDE dari [arduino.cc](https://www.arduino.cc/en/software)
2. Install driver CH340 (jika menggunakan board clone)
3. Buka Arduino IDE dan install library berikut:
   - **Built-in Library** (sudah termasuk):
     - `Wire` (untuk komunikasi I2C)
     - `Servo` (untuk kontrol servo motor)
   
   - **Library Tambahan** (harus diinstall):
     1. Buka Tools > Manage Libraries...
     2. Cari dan install:
        - `LiquidCrystal I2C` by Frank de Brabander
        - `DFRobot DHT11` by DFRobot

4. Buka file `robot.ino` di Arduino IDE

### 4. Download Model (sekali saja)
```bash
# Download model Whisper (akan diunduh otomatis saat pertama kali dijalankan)
python -c "import whisper; model = whisper.load_model('tiny')"

# Download model NeuroBERT untuk pemrosesan bahasa
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
    tokenizer = AutoTokenizer.from_pretrained('boltuix/NeuroBERT-Mini'); \
    model = AutoModelForSequenceClassification.from_pretrained('boltuix/NeuroBERT-Mini')"

# Verifikasi instalasi
python -c "import torch; print(f'CUDA tersedia: {torch.cuda.is_available()}')"
{{ ... }}
| Buzzer    | 6           | Speaker/buzzer      |
| DHT11     | 5           | Sensor suhu/kelembaban|
| LCD SDA   | A4          | I2C data            |
| LCD SCL   | A5          | I2C clock           |

## 🎨 Tema dan Gaya Website

### Warna Utama:
```css
:root {
  --primary: #4a6bff;
  --secondary: #6c757d;
  --success: #28a745;
  --danger: #dc3545;
  --light: #f8f9fa;
  --dark: #343a40;
  --bg-light: #f5f7ff;
  --bg-dark: #1a1a2e;
  --text-light: #f8f9fa;
  --text-dark: #212529;
}
```

### Font yang Digunakan:
- **Utama**: 'Segoe UI', system-ui, -apple-system, sans-serif
- **Judul**: 'Poppins', sans-serif
- **Kode**: 'Fira Code', 'Courier New', monospace

### Komponen UI:
1. **Tombol Mikrofon**
   - Animasi pulse saat merekam
   - Efek hover dan active state
   - Indikator visual status rekaman

2. **Kartu Hasil**
   - Shadow effect untuk depth
   - Transisi halus
   - Responsif di berbagai ukuran layar

3. **Status Koneksi**
   - Indikator warna (hijau/merah)
   - Animasi pulse saat terhubung
   - Tooltip informatif

## 🚀 CARA MENJALANKAN STEP BY STEP

### 1. Upload Kode ke Arduino
1. Sambungkan Arduino ke komputer
2. Buka file `robot.ino` di Arduino IDE
3. Pilih board:
   - Tools > Board > Arduino AVR Boards > Arduino Uno
4. Pilih port COM (di Windows) atau /dev/tty* (di Mac/Linux)
5. Klik tombol Upload (panah kanan) atau Ctrl+U
6. Tunggu sampai muncul "Done uploading"

### 2. Install Dependensi Web
Pastikan semua dependensi web sudah terinstall:
```bash
pip install flask flask-cors
```

### 3. Jalankan Aplikasi Python

#### A. Mode Terminal (Tanpa Web Interface)
```bash
python stt_ai.py
```

#### B. Mode Web Interface (Dengan Mikrofon)
1. Pastikan dependensi web sudah terinstall:
   ```bash
   pip install flask flask-cors
   ```
2. Jalankan aplikasi dengan perintah:
   ```bash
   python stt_ai.py --web
   ```
3. Buka browser dan kunjungi: http://localhost:4141
4. Klik tombol mikrofon dan mulai berbicara

### 4. Perintah yang Didukung

#### Kontrol LED
- "Nyalakan lampu merah"
- "Matikan lampu merah"
- "Nyalakan semua lampu"
- "Matikan semua lampu"

#### Kontrol Suara
- "Bunyikan speaker"
- "Bunyikan alarm"

#### Sensor
- "Berapa suhu sekarang?"
- "Berapa kelembaban?"

#### Kontrol Motor
- "Putar servo"
- "Putar kanan"
- "Putar kiri"
```

### 3. Test Koneksi
Setelah menjalankan, coba perintah berikut di terminal:
```bash
# Test LED
L13:1:2  # Nyalakan LED merah 2 detik

# Test Buzzer
S1000:1  # Bunyikan buzzer 1000Hz 1 detik
```

### 3. Uji Perintah Suara
- "Nyalakan lampu"
- "Matikan lampu"
- "Putar servo"
- "Berapa suhu?"
- "Tampilkan halo di layar"

## 🎤 CONTOH PERINTAH SUARA

### Kontrol LED
- "Nyalakan lampu" → LED 13 ON
- "Nyalakan lampu biru" → LED 9 ON
- "Matikan semua lampu" → Semua LED OFF
- "Kedip-kedip lampu" → LED berkedip

### Servo
- "Putar servo" → Putar 90 derajat
- "Putar kiri" → Putar ke kiri
- "Putar kanan" → Putar ke kanan

### Sensor
- "Berapa suhu?" → Baca suhu
- "Berapa kelembaban?" → Baca kelembaban

### LCD
- "Tampilkan halo" → Tampilkan teks di LCD
- "Bersihkan layar" → Hapus teks di LCD

## 🐛 TROUBLESHOOTING

### Suara Tidak Terdeteksi
1. Pastikan mikrofon terhubung
2. Periksa izin mikrofon di pengaturan sistem
3. Coba perintah lebih lantang

### Arduino Tidak Terdeteksi
1. Periksa kabel USB
2. Pastikan port COM yang benar di `stt_ai.py` (baris 18)
3. Restart Arduino IDE

### Error Library
```bash
# Jika error sounddevice di Windows
pip install pipwin
pipwin install pyaudio

# Jika error di Linux
sudo apt-get install portaudio19-dev
```

## 🔍 CODE REVIEW

### 1. voice_robot.py
- ✅ Baik: Kode sederhana dan mudah dimengerti
- ✅ Baik: Menggunakan whisper untuk speech-to-text
- 💡 Saran: Tambahkan error handling untuk kasus mikrofon tidak terdeteksi

### 2. stt_ai.py
- ✅ Baik: Menggunakan GPT-2 untuk pemrosesan bahasa alami
- 💡 Saran: Tambahkan komentar lebih banyak untuk menjelaskan logika AI

### 3. robot.ino
- ✅ Baik: Kode terstruktur dengan baik
- ✅ Baik: Memiliki handler terpisah untuk setiap komponen
- 💡 Saran: Tambahkan komentar untuk menjelaskan fungsi-fungsi handler

## 📝 CATATAN
- Pastikan Arduino terhubung sebelum menjalankan `stt_ai.py`
- Untuk hasil terbaik, gunakan di lingkungan yang tenang
- Kalibrasi servo jika diperlukan di kode `robot.ino`

## 🔄 UPDATE TERAKHIR
- 7 Oktober 2025: 
  - Menambahkan panduan lengkap instalasi
  - Menambahkan web interface
  - Menyederhanakan perintah suara
  - Menghapus ketergantungan API key

Selamat mencoba! 🤖✨
