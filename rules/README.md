# Panduan Menjalankan Robot AI

Selamat datang di Robot AI Universe!  
Di sini kamu bakal belajar gimana caranya ngebuat Arduino dan AI ngobrol kayak dua sahabat yang sering debat tapi tetep akur.

---

## 1. Persiapan Dulu!

### Yang wajib kamu punya:
- Arduino IDE (buat upload kode ke si robot)
- Python 3.10+ (buat otak AI-nya)
- Library Arduino: `Servo`, `LCD_I2C`, `DFRobot_DHT11`, `Wire`
- Library Python: `pyserial`, `flask`, `transformers`, `torch`, `sounddevice`, `scipy`, `numpy`

Kalau belum, install dulu biar gak dibilang "noob" sama Arduino-nya

---

## 2. Upload Kode ke Arduino

1. Buka Arduino IDE  
2. Pilih file `robot.ino`
3. Klik **Tools → Board → Arduino Uno**  
4. Klik **Tools → Port → COM3** (atau port yang muncul)  
5. Terakhir, pencet tombol **Upload (→)** dan tunggu sampai muncul tulisan:  
   > *Done uploading.*

---

## 3. Aktifin Otak Python-nya

Buka **CMD / Terminal**, masuk ke folder proyek kamu:
```bash
cd C:\Users\acer\Documents\RobotAI
```

### Buat Virtual Environment
```bash
python -m venv venv
```

### Aktifin
```bash
venv\Scripts\activate
```

### Install semua library yang dibutuhkan
```bash
pip install pyserial flask transformers torch sounddevice scipy numpy
```

---

## 4. Jalankan Server AI

Masih di CMD yang sama:
```bash
python web_interface.py
```

Kalau muncul:
```
Server running on http://localhost:4141
Connected to Arduino on COM3
```
Berarti server sudah berjalan dengan baik.

---

## 5. Buka Dashboard

Buka browser kamu → ketik:
```
http://localhost:4141
```

---

## 6. Coba Kirim Perintah Manual

Langsung di web interface atau lewat Python:

```python
robot.send_command("L13:1:3")  # LED nyala 3 detik
robot.send_command("S500:2")   # Buzzer bunyi 500Hz 2 detik
robot.send_command("TR")       # Baca suhu dan tampil di LCD
```

Atau bisa juga di **Serial Monitor** Arduino:
```
L13:1:3
TR
