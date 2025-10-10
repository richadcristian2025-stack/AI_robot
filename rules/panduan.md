# 🤖 Voice Controlled Robot - Setup Guide

Panduan lengkap untuk setup dan menjalankan Voice Controlled Robot dengan AI.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Hardware Requirements](#hardware-requirements)
3. [Software Requirements](#software-requirements)
4. [Installation](#installation)
5. [Project Structure](#project-structure)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)
9. [Usage Guide](#usage-guide)

---

## 💻 System Requirements

### Minimum Requirements:
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.15+
- **CPU**: Intel Core i3 atau AMD Ryzen 3 (2 cores)
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **USB Port**: 1 port untuk Arduino
- **Microphone**: Built-in atau external
- **Browser**: Chrome, Firefox, Edge (latest version)

### Recommended Requirements:
- **OS**: Windows 11 atau Ubuntu 22.04
- **CPU**: Intel Core i5 atau AMD Ryzen 5 (4+ cores)
- **RAM**: 8 GB
- **Storage**: 5 GB free space
- **GPU**: NVIDIA GPU dengan CUDA support (optional, untuk faster processing)
- **USB Port**: USB 3.0
- **Microphone**: External microphone untuk kualitas lebih baik

---

## 🔧 Hardware Requirements

### 1. Arduino Board
- **Arduino Uno** (Recommended)
- **Arduino Mega 2560**
- **Arduino Nano**
- **Arduino compatible boards**

### 2. Components (Opsional, tergantung project)
- LED (untuk testing)
- Motor DC (untuk robot bergerak)
- Motor Driver (L298N, L293D)
- Buzzer/Speaker (untuk sound)
- DHT11/DHT22 (untuk sensor suhu & kelembaban)
- Jumper wires
- Breadboard
- Power supply (9V battery atau adaptor)

### 3. Kabel USB
- USB Type-A to Type-B (untuk Arduino Uno/Mega)
- USB Type-A to Mini-USB (untuk Arduino Nano)

### 4. Komputer/Laptop
- Dengan port USB available
- Microphone (built-in atau external)
- Speaker (untuk feedback audio)

---

## 📦 Software Requirements

### 1. Python
**Version**: Python 3.8 - 3.11 (Recommended: 3.10)

**Download**: https://www.python.org/downloads/

**Installation Check**:
```bash
python --version
# Output: Python 3.10.x
```

**Catatan**: 
- ✅ Centang "Add Python to PATH" saat install
- ❌ Jangan gunakan Python 3.12 (belum compatible dengan beberapa library)

---

### 2. Arduino IDE
**Version**: Arduino IDE 2.x atau 1.8.x

**Download**: https://www.arduino.cc/en/software

**Installation Check**:
- Buka Arduino IDE
- Tools → Board → Arduino Uno (pilih board yang kamu gunakan)
- Tools → Port → COM3 (atau port yang terdeteksi)

---

### 3. Git (Optional)
**Version**: Latest

**Download**: https://git-scm.com/downloads

**Installation Check**:
```bash
git --version
# Output: git version 2.x.x
```

---

## 📚 Python Libraries Required

### Core Libraries:

| Library | Version | Fungsi | Size |
|---------|---------|--------|------|
| `flask` | 3.0.0 | Web framework | ~1 MB |
| `flask-cors` | 4.0.0 | CORS support | ~50 KB |
| `torch` | 2.1.0+ | PyTorch untuk AI | ~800 MB |
| `transformers` | 4.35.0+ | Hugging Face models | ~500 MB |
| `pyserial` | 3.5 | Serial communication | ~100 KB |
| `numpy` | 1.24.3 | Array processing | ~20 MB |
| `sounddevice` | 0.4.6 | Audio recording | ~1 MB |
| `wavio` | 0.0.8 | WAV file handling | ~10 KB |
| `scikit-learn` | 1.3.0 | Machine Learning | ~30 MB |

### Total Download Size: **~1.5 GB**

---

## 🚀 Installation

### Step 1: Install Python

**Windows:**
1. Download Python installer dari python.org
2. Run installer
3. ✅ Centang "Add Python to PATH"
4. Klik "Install Now"

**Linux:**
```bash
sudo apt update
sudo apt install python3.10 python3-pip
```

**macOS:**
```bash
brew install python@3.10
```

**Verify:**
```bash
python --version
pip --version
```

---

### Step 2: Download Project

**Option A: Git Clone**
```bash
git clone https://github.com/yourusername/voice-robot.git
cd voice-robot
```

**Option B: Download ZIP**
1. Download ZIP dari repository
2. Extract ke folder
3. Buka terminal di folder tersebut

---

### Step 3: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify virtual env active:**
```bash
# Terminal akan menampilkan (venv) di awal
(venv) C:\voice-robot>
```

---

### Step 4: Install Python Libraries

**Install semua dependencies:**
```bash
pip install -r requirements.txt
```

**Atau install manual satu-satu:**
```bash
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install torch==2.1.0
pip install transformers==4.35.0
pip install pyserial==3.5
pip install numpy==1.24.3
pip install sounddevice==0.4.6
pip install wavio==0.0.8
pip install scikit-learn==1.3.0
```

**Download Whisper Model (otomatis saat run pertama kali):**
```bash
# Model akan di-download otomatis (~39 MB untuk "tiny")
# Lokasi: C:\Users\YourName\.cache\whisper\
```

**Verify installation:**
```bash
pip list
# Check if all libraries installed
```

**Troubleshooting:**

**Error torch not found:**
```bash
# Install dari PyTorch website sesuai system
# CPU only:
pip install torch --index-url https://download.pytorch.org/whl/cpu

# With CUDA (GPU):
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Error sounddevice:**
```bash
# Windows: Install Microsoft Visual C++ Redistributable
# Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

### Step 5: Install Arduino IDE

1. Download Arduino IDE dari arduino.cc
2. Install dengan default settings
3. Buka Arduino IDE
4. Install board drivers jika diperlukan

**Windows:** Driver akan auto-install

**Linux:**
```bash
sudo usermod -a -G dialout $USER
# Logout & login lagi
```

---

### Step 6: Upload Arduino Code

1. Buka Arduino IDE
2. File → Open → `arduino/robot.ino`
3. Tools → Board → Arduino Uno (atau board kamu)
4. Tools → Port → COM3 (pilih port yang terdeteksi)
5. Upload code (Ctrl+U)

**Verify upload:**
```
Sketch uses X bytes (X%) of program storage space.
Global variables use Y bytes (Y%) of dynamic memory.
Done uploading.
```

**Check COM Port:**

**Windows:**
```
Device Manager → Ports (COM & LPT) → Arduino Uno (COM3)
```

**Linux:**
```bash
ls /dev/tty*
# Look for /dev/ttyUSB0 or /dev/ttyACM0
```

**macOS:**
```bash
ls /dev/tty.*
# Look for /dev/tty.usbserial-* or /dev/tty.usbmodem*
```

---

## 📁 Project Structure

```
voice_robot_project/
│
├── web_interface.py              # Main web application
├── voice_robot.py                # Terminal mode application
├── simple_ai.py                  # Simple AI engine
├── ml_ai.py                      # Machine Learning AI
├── stt_ai.py                     # Reference code
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── SETUP_GUIDE.md               # This file
│
├── templates/
│   └── index.html                # Web UI
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── style-new.css
│   │   └── style-beautiful.css
│   └── js/
│       └── app.js (optional)
│
└── arduino/
    └── robot.ino                 # Arduino sketch
```

---

## ⚙️ Configuration

### 1. Edit `web_interface.py`

**Set Arduino Port:**
```python
# Line ~30
ARDUINO_PORT = "COM3"  # Windows
# ARDUINO_PORT = "/dev/ttyUSB0"  # Linux
# ARDUINO_PORT = "/dev/tty.usbserial"  # macOS
```

**Set Web Port:**
```python
# Line ~32
WEB_PORT = 4141  # Ubah jika port sudah dipakai
```

**Select AI Engine:**
```python
# Line ~40
from simple_ai import SimpleRobotAI  # Simple AI
# from ml_ai import MLRobotAI  # Atau ML AI
```

---

### 2. Edit `arduino/robot.ino`

**Set Serial Baud Rate:**
```cpp
void setup() {
    Serial.begin(9600);  # Harus sama dengan Python (9600)
    // ...
}
```

**Configure Pins:**
```cpp
#define LED_PIN 13
#define MOTOR_LEFT_PIN1 5
#define MOTOR_LEFT_PIN2 6
// ... sesuaikan dengan wiring kamu
```

---

## 🎮 Running the Application

### Method 1: Web Interface (Recommended)

**1. Activate Virtual Environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**2. Run Web Server:**
```bash
python web_interface.py
```

**Expected Output:**
```
============================================================
🤖 Initializing Voice Controlled Robot System...
============================================================
🧠 Loading Whisper model (openai/whisper-tiny) on cpu...
✅ Whisper model loaded successfully
✅ Arduino connected on COM3

============================================================
🌐 Starting web server...
📡 Access the interface at: http://localhost:4141
============================================================

 * Serving Flask app 'web_interface'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://0.0.0.0:4141
```

**3. Open Browser:**
```
http://localhost:4141
```

**4. Test Voice Control:**
- Klik tombol mikrofon 🎤
- Ucapkan perintah: "nyalakan lampu"
- Tunggu processing
- LED Arduino akan menyala!

---

### Method 2: Terminal Mode (No Browser)

**1. Run Voice Robot:**
```bash
python voice_robot.py
```

**Expected Output:**
```
============================================================
🤖 VOICE ROBOT - LOCAL CONTROL
============================================================
🧠 Memuat model Whisper (tiny)...
✅ Model 'tiny' siap digunakan!

🔍 Mencari Arduino...
✅ Arduino ditemukan: COM3
✅ Arduino terhubung di COM3

💡 PERINTAH SUARA YANG TERSEDIA:
============================================================
🔦 Lampu: nyala, hidup, matikan, mati
🚗 Gerakan: maju, mundur, kiri, kanan, berhenti
🌡️ Sensor: suhu, kelembaban
🔔 Suara: alarm, bel, bunyi
============================================================

🎙️  Tekan ENTER untuk mulai merekam
⌨️  Ketik 'q' untuk keluar
⌨️  Ketik 'c' untuk lihat perintah

------------------------------------------------------------

>>> Tekan ENTER untuk merekam (atau q/c): 
```

**2. Test:**
- Press ENTER
- Speak: "nyalakan lampu"
- Wait for processing
- Arduino executes command

---

### Method 3: Test AI Only (No Arduino)

**Simple AI Test:**
```bash
python simple_ai.py
```

**ML AI Test:**
```bash
python ml_ai.py
```

---

## 🐛 Troubleshooting

### Problem 1: Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Method 1: Ubah port di web_interface.py
WEB_PORT = 4142  # Ganti dari 4141

# Method 2: Kill process yang pakai port 4141
# Windows:
netstat -ano | findstr :4141
taskkill /PID <PID_NUMBER> /F

# Linux:
lsof -i :4141
kill -9 <PID>
```

---

### Problem 2: Arduino Not Detected

**Error:**
```
⚠️ Arduino not found. Running in SIMULATION mode.
```

**Solution:**

**Windows:**
1. Cek Device Manager → Ports
2. Install Arduino drivers
3. Coba port lain: COM4, COM5, etc

**Linux:**
```bash
# Check permissions
sudo usermod -a -G dialout $USER
# Logout & login

# Check devices
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*
```

**Check in Python:**
```python
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device, port.description)
```

---

### Problem 3: Whisper Model Not Loading

**Error:**
```
❌ Failed to load Whisper model
```

**Solution:**
```bash
# Re-download model
python -c "import whisper; whisper.load_model('tiny')"

# Check storage space (need ~500MB free)
# Clear cache if needed
# Windows: C:\Users\YourName\.cache\whisper\
# Linux: ~/.cache/whisper/
```

---

### Problem 4: Microphone Not Working

**Error:**
```
❌ Gagal mengakses mikrofon
```

**Solution:**

**Windows:**
```
Settings → Privacy → Microphone
- Allow apps to access microphone: ON
- Allow Chrome/Firefox: ON
```

**Linux:**
```bash
# Check audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav
aplay test.wav
```

**Browser:**
- Use HTTPS or localhost only
- Check browser microphone permissions
- Try different browser

---

### Problem 5: Torch/CUDA Issues

**Error:**
```
torch not available with CUDA
```

**Solution:**
```bash
# CPU only (no GPU needed):
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu

# With CUDA (if you have NVIDIA GPU):
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

### Problem 6: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Check virtual env active
# Should see (venv) in terminal

# Re-install requirements
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.executable)"
```

---

## 📖 Usage Guide

### Voice Commands:

| Category | Commands (ID) | Commands (EN) | Arduino Code |
|----------|---------------|---------------|--------------|
| **Lights** | nyala, hidup, nyalakan | on, light on | L13:1:5 |
| | mati, matikan, padam | off, light off | L13:0:0 |
| **Movement** | maju, kedepan | forward | MF:90:1 |
| | mundur, kebelakang | backward | MB:90:1 |
| | kiri, belok kiri | left, turn left | ML:90:1 |
| | kanan, belok kanan | right, turn right | MR:90:1 |
| | berhenti, stop | stop | MS:0:0 |
| **Sensors** | suhu, temperatur | temperature | TR |
| | kelembaban | humidity | HR |
| **Sound** | alarm, sirine | alarm, siren | S1000:1 |
| | bunyi, beep | beep, sound | S1000:1 |

### Web Interface:

1. **Check Connection Status** (top right)
   - 🟢 Green = Connected
   - 🔴 Red = Simulation Mode

2. **Record Voice:**
   - Click microphone button
   - Speak clearly (5 seconds max)
   - Wait for processing
   - See result & response

3. **Use Suggestion Chips:**
   - Click suggestion buttons for quick commands
   - No voice needed

4. **View History:**
   - See last 10 commands
   - Check responses

### Terminal Mode:

```bash
>>> Tekan ENTER untuk merekam (atau q/c): [ENTER]

🎤 Bicara sekarang (5 detik)...
[Speak: "nyalakan lampu"]
✅ Selesai merekam.
🔊 Memproses suara...
🗣️  Kamu bilang: 'nyalakan lampu'
✅ Perintah ditemukan: 'nyala' → L13:1:5
🤖 Respon: OK

------------------------------------------------------------

>>> Tekan ENTER untuk merekam (atau q/c): q
👋 Keluar dari program...
```

---

## 🔐 Security Notes

⚠️ **Important:**

1. **Development Server**: Flask development server is NOT for production
2. **Network**: Only use on trusted networks
3. **Firewall**: Port 4141 akan open untuk local network
4. **Arduino**: Jangan hubungkan ke high-voltage devices tanpa proper isolation

---

## 📞 Support

**Issues?** Create issue di GitHub repository

**Documentation:** https://github.com/richadcristian2025-stack/AI_robot

---

## 📝 License

MIT License - Free to use and modify

---

## 🎉 Success Indicators

Jika semua berjalan dengan baik, kamu akan melihat:

✅ Python 3.10 installed
✅ All libraries installed (`pip list`)
✅ Arduino IDE can upload code
✅ COM port detected (Device Manager)
✅ Web server running on port 4141
✅ Browser can access http://localhost:4141
✅ Microphone permission granted
✅ Whisper model loaded successfully
✅ Arduino responds to commands
✅ LED/Motor works as expected

---

**Last Updated:** 2025-01-10
**Version:** 1.0.0
**Author:** Chadd
