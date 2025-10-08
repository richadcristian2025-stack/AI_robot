# 📚 Panduan Lengkap Robot AI dengan Arduino

## 🏁 Daftar Isi
1. [Pendahuluan](#-pendahuluan)
2. [Daftar Komponen](#-daftar-komponen)
3. [Instalasi Perangkat Lunak](#-instalasi-perangkat-lunak)
4. [Pemasangan Hardware](#-pemasangan-hardware)
5. [Upload Kode ke Arduino](#-upload-kode-ke-arduino)
6. [Menjalankan Aplikasi Python](#-menjalankan-aplikasi-python)
7. [Daftar Perintah Suara](#-daftar-perintah-suara)
8. [Troubleshooting](#-troubleshooting)
9. [FAQ](#-faq)

## 🌟 Pendahuluan
Robot AI ini dikendalikan melalui perintah suara menggunakan pemrosesan bahasa alami dan dapat menampilkan berbagai informasi melalui LCD. Robot dilengkapi dengan sensor suhu/kelembaban DHT11, LED indikator, buzzer, dan servo motor.

## 📋 Daftar Komponen
### Komponen Wajib
- [ ] 1x Arduino Uno
- [ ] 5x LED (Merah, Kuning, Hijau, Biru, Putih)
- [ ] 1x Buzzer/Speaker
- [ ] 1x Servo Motor (SG90/MG90S)
- [ ] 1x Sensor DHT11
- [ ] 1x LCD 16x2 I2C
- [ ] 1x Breadboard
- [ ] Kabel Jumper (Male-Male, Male-Female)
- [ ] Resistor 220Ω (5 pcs)
- [ ] Kabel USB Arduino

### Komponen Opsional
- [ ] Potensiometer 10kΩ
- [ ] Power Bank/Adaptor 5V 2A

## 💻 Instalasi Perangkat Lunak

### 1. Instal Python
1. Download Python 3.8+ dari [python.org](https://www.python.org/downloads/)
2. Saat instalasi, centang "Add Python to PATH"
3. Verifikasi instalasi dengan buka CMD dan ketik:
   ```bash
   python --version
   pip --version
   ```

### 2. Instal Library Python
Buka CMD/terminal dan jalankan:
```bash
# Buat virtual environment
python -m venv venv
venv\Scripts\activate

# Install library utama
pip install torch torchaudio transformers flask flask-cors python-dotenv

# Untuk pemrosesan audio
pip install sounddevice wave soundfile
pip install pipwin
pipwin install pyaudio
```

### 3. Instal Arduino IDE
1. Download Arduino IDE dari [arduino.cc](https://www.arduino.cc/en/software)
2. Install driver CH340 (jika menggunakan board clone)
3. Buka Arduino IDE dan install library berikut:
   - DFRobot_DHT11
   - LiquidCrystal I2C
   - Servo

## 🔌 Pemasangan Hardware

### Diagram Rangkaian
```
+----------------+      +-----------------+
|     Arduino    |      |      LCD        |
|                |      |                 |
| 5V  -----------+------> VCC            |
| GND -----------+------> GND            |
| A4  -----------+------> SDA            |
| A5  -----------+------> SCL            |
| D2  <----------+------ DATA (DHT11)    |
| D6  -----------+------> Buzzer(+)      |
| D7  -----------+------> Servo Signal   |
| D8  -----------+------> LED Putih      |
| D9  -----------+------> LED Biru       |
| D10 -----------+------> LED Hijau      |
| D11 -----------+------> LED Kuning     |
| D12 -----------+------> (Tidak terpakai)|
| D13 -----------+------> LED Merah      |
+----------------+      +-----------------+
```

### Langkah Pemasangan
1. Pasang LCD I2C di breadboard
2. Hubungkan DHT11 ke pin D2
3. Hubungkan LED dengan resistor 220Ω ke pin masing-masing
4. Hubungkan buzzer ke pin D6
5. Hubungkan servo ke pin D7
6. Hubungkan semua ground (GND) ke breadboard
7. Hubungkan semua VCC (5V) ke breadboard

## ⚡ Upload Kode ke Arduino
1. Buka file `robot.ino` di Arduino IDE
2. Pilih board "Arduino Uno" di Tools > Board
3. Pilih port COM yang sesuai
4. Klik tombol Upload (panah kanan)
5. Tunggu hingga muncul pesan "Done uploading"

## 🚀 Menjalankan Aplikasi Python
1. Buka terminal di folder project
2. Aktifkan virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Jalankan aplikasi:
   ```bash
   python stt_ai.py
   ```
4. Untuk mode web, gunakan:
   ```bash
   python stt_ai.py --web
   ```
5. Buka browser dan akses `http://localhost:4141`

## 🎤 Daftar Perintah Suara
### Kontrol LED
- "Nyalakan lampu" - Menyalakan LED merah
- "Matikan lampu" - Mematikan LED merah
- "Buat lampu berkedip" - Semua LED berkedip

### Sensor
- "Berapa suhu?" - Menampilkan suhu di LCD
- "Berapa kelembaban?" - Menampilkan kelembaban di LCD

### Gerakan
- "Maju" - Servo bergerak maju
- "Mundur" - Servo bergerak mundur
- "Kanan" - Servo ke kanan
- "Kiri" - Servo ke kiri
- "Berhenti" - Menghentikan semua gerakan

### Suara
- "Bunyikan alarm" - Mengaktifkan buzzer
- "Bunyikan nada 500" - Bunyi dengan frekuensi 500Hz

## 🔧 Troubleshooting
### Jika DHT11 Tidak Terbaca
1. Pastikan koneksi ke pin D2 benar
2. Ganti kabel jika perlu
3. Periksa apakah library DHT11 sudah terinstall

### Jika Suara Tidak Terdeteksi
1. Periksa mikrofon di pengaturan Windows
2. Pastikan PyAudio terinstall dengan benar
3. Coba ganti perangkat input di kode

### Jika LCD Kosong
1. Periksa koneksi I2C
2. Cek tegangan di VCC (harus 5V)
3. Putar potensiometer di modul I2C untuk menyesuaikan kontras

## ❓ FAQ
### Q: Bagaimana cara mengubah sensitivitas suara?
A: Ubah parameter `energy_threshold` di file `stt_ai.py`

### Q: Bisakah menambah perintah suara baru?
A: Ya, tambahkan di dictionary `command_mapping` di file `stt_ai.py`

### Q: Berapa jarak maksimal suara bisa dideteksi?
A: Sekitar 1-2 meter dengan mikrofon internal, bisa lebih jauh dengan mikrofon eksternal

### Q: Bagaimana cara reset semua pengaturan?
A: Tekan tombol reset di Arduino atau cabut dan pasang kembali kabel USB

## 📝 Catatan
- Pastikan koneksi kabel rapi dan aman
- Gunakan power supply yang memadai jika menggunakan banyak komponen
- Backup kode secara berkala

## 📞 Dukungan
Jika mengalami masalah, buat issue di [GitHub](https://github.com/username/repo) atau hubungi:
- Email: your.email@example.com
- WhatsApp: +62812-3456-7890

---
Dibuat dengan ❤️ oleh Tim RobotAI | © 2025
