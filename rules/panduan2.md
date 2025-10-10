
# 🤖 Panduan Menjalankan Robot AI (Versi Lucu & Nggak Bikin Ngantuk)

Selamat datang di **Robot AI Universe!** 🎉  
Di sini kamu bakal belajar gimana caranya ngebuat Arduino dan AI ngobrol kayak dua sahabat yang sering debat tapi tetep akur.

---

## 🧩 1. Persiapan Dulu, Bro!

### Yang wajib kamu punya:
- 💻 Arduino IDE (buat upload kode ke si robot)
- 🐍 Python 3.10+ (buat otak AI-nya)
- ⚙️ Library Arduino: `Servo`, `LCD_I2C`, `DFRobot_DHT11`, `Wire`
- 📦 Library Python: `pyserial`, `flask`, `transformers`, `torch`, `sounddevice`, `scipy`, `numpy`

Kalau belum, install dulu biar gak dibilang “noob” sama Arduino-nya 😎

---

## ⚡ 2. Upload Kode ke Arduino

1. Buka Arduino IDE  
2. Pilih file `robot.ino`
3. Klik **Tools → Board → Arduino Uno**  
4. Klik **Tools → Port → COM3** (atau port yang muncul)  
5. Terakhir, pencet tombol **Upload (→)** dan tunggu sampai muncul tulisan:  
   > ✅ *Done uploading.*  

Selamat! Arduino kamu sekarang punya jiwa. 💡

---

## 🧠 3. Aktifin Otak Python-nya

Buka **CMD / Terminal**, masuk ke folder proyek kamu:
```bash
cd C:\Users\acer\Documents\RobotAI
```

### Buat Virtual Environment
```bash
python -m venv venv
```

### Aktifin (biar gak error)
```bash
venv\Scripts\activate
```

### Install semua otak tambahan
```bash
pip install pyserial flask transformers torch sounddevice scipy numpy
```

Kalau semua udah terinstal, siap lanjut gas! 🚀

---

## 🧮 4. Jalankan Server AI

Masih di CMD yang sama:
```bash
python web_interface.py
```

Kalau muncul:
```
🚀 Server running on http://localhost:4141
✅ Connected to Arduino on COM3
```
Berarti kamu udah resmi punya asisten pribadi versi robot 😎

---

## 🌐 5. Buka Dashboard

Buka browser kamu → ketik:
```
http://localhost:4141
```

Tadaaa! 🎉 Muncul UI cantik buat ngontrol robotmu.

---

## 🧪 6. Coba Kirim Perintah Manual

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
D:Hello Dunia!
```

Kalau semua hidup, selamat! Kamu baru aja bikin robot yang bisa disuruh lewat AI 🔥

---

## 🎤 7. Mode Suara Aktif!

Kalau di web ada tombol 🎙️, tekan → ngomong → tunggu →  
Robot bakal nurut (asal bukan disuruh “buat kopi” ☕).

---

## ⚙️ 8. Masalah? Tenang...

| Masalah | Solusi |
|----------|---------|
| ❌ Serial error | Ganti COM port di `web_interface.py` |
| 💀 LCD blank | Coba alamat `0x27` atau `0x3F` |
| 🌡️ DHT11 ga baca suhu | Cek kabel data & ground |
| 🦾 Servo diam | Kasih power supply tambahan (jangan cuma dari 5V Arduino) |

---

## 🏁 9. Penutupan Gagah

Kalau semua udah jalan, sekarang kamu bisa:
> 🎤 Bicara → 🧠 AI denger → ⚡ Arduino gerak → 🤖 Dunia kagum.

Selamat, kamu udah jadi **Pawang Robot AI 3000** 🤓⚡  
Sekarang tinggal kasih nama robotmu. (Saran: “Si OyenBot” 🐱)

---

**Dibuat oleh:** Kamu sendiri, sang master robot.  
**Dibantu oleh:** ChatGPT (asisten yang gak pernah ngeluh 😆)
