# 🧠 Arduino Smart Robot Hardware Setup

Proyek ini menggunakan berbagai komponen elektronik yang terhubung ke Arduino Uno.  
Semua komponen dikendalikan melalui perintah serial seperti **L**, **S**, **M**, **TR**, **HR**, dan **D:** sesuai dengan kode program.

---

## ⚙️ Daftar Komponen

| No | Komponen | Jumlah | Fungsi Utama |
|----|-----------|---------|---------------|
| 1 | Arduino Uno | 1 | Mikrokontroler utama yang menjalankan program |
| 2 | LED (Merah, Kuning, Hijau, Biru, Putih) | 5 | Indikator status dan notifikasi visual |
| 3 | Buzzer / Speaker | 1 | Mengeluarkan suara (nada atau peringatan) |
| 4 | Servo Motor (SG90 atau MG90S) | 1 | Menggerakkan bagian mekanik (misalnya tangan robot) |
| 5 | Sensor DHT11 | 1 | Mengukur suhu dan kelembaban lingkungan |
| 6 | LCD 16x2 I2C | 1 | Menampilkan teks status, hasil sensor, atau pesan |
| 7 | Potensiometer 10kΩ (opsional) | 1 | Mengatur posisi servo secara manual |
| 8 | Breadboard + Kabel Jumper | - | Untuk merangkai semua komponen |

---

## 🔌 Tabel Koneksi Pin Arduino

| Komponen | Pin Arduino | Jenis Pin | Keterangan |
|-----------|--------------|------------|-------------|
| **LED Merah** | D13 | Digital Output | Indikator utama |
| **LED Kuning** | D11 | Digital Output | Indikator status |
| **LED Hijau** | D10 | Digital Output | Indikator kondisi normal |
| **LED Biru** | D9 | Digital Output | Indikator mode tertentu |
| **LED Putih** | D8 | Digital Output | Indikator umum |
| **Buzzer / Speaker** | D6 | Digital Output (tone) | Mengeluarkan suara dengan perintah `S500:2` |
| **Servo Motor** | D7 | PWM Output | Menggerakkan servo dengan perintah `MF:180:2` |
| **Sensor DHT11** | D2 | Digital Input | Membaca suhu dan kelembaban (ubah dari pin 11 agar tidak konflik) |
| **LCD SDA** | A4 | I2C | Komunikasi data LCD |
| **LCD SCL** | A5 | I2C | Sinkronisasi data LCD |
| **Potensiometer (opsional)** | A0 | Analog Input | Membaca nilai rotasi (0–1023) untuk kontrol servo manual |
| **VCC (Semua Komponen)** | 5V | Power | Sumber daya 5 volt |
| **GND (Semua Komponen)** | GND | Ground | Jalur negatif listrik |

---

## 🧩 Rincian Komponen

### 1. LED
- Gunakan resistor 220–330Ω pada setiap LED.
- Warna LED disesuaikan agar mudah dibedakan fungsi visualnya.

### 2. Buzzer / Speaker
- Tipe: Buzzer aktif atau pasif.
- Dikendalikan dengan fungsi `tone()` dan `noTone()` di pin D6.

### 3. Servo Motor
- Tipe: SG90 (servo kecil 180°) atau servo continuous.
- Jika servo berputar lemah, gunakan power eksternal 5V terpisah dari pin Arduino.

### 4. Sensor DHT11
- Gunakan library `DFRobot_DHT11`.
- Output berupa **Suhu (°C)** dan **Kelembaban (%)**.
- Di kode: otomatis menyalakan LED hijau/biru tergantung suhu.

### 5. LCD 16x2 I2C
- Library: `LCD_I2C.h`
- Alamat default I2C: `0x27`
- Menampilkan teks, hasil sensor, dan status robot.
- Koneksi:
  - **VCC → 5V**
  - **GND → GND**
  - **SDA → A4**
  - **SCL → A5**

### 6. Potensiometer (Opsional)
- Koneksi:
  - **Kaki kiri → GND**
  - **Kaki tengah → A0**
  - **Kaki kanan → 5V**
- Nilai dibaca dengan `analogRead(A0)` untuk kontrol servo manual.

---

## 💬 Contoh Perintah Serial

| Perintah | Fungsi | Contoh |
|-----------|---------|---------|
| `L13:1:5` | Nyalakan LED pin 13 selama 5 detik | 🔴 LED merah hidup |
| `LA:2:3` | Semua LED berkedip selama 3 detik | ✨ Semua LED blink |
| `S500:2` | Bunyi buzzer 500Hz selama 2 detik | 🔊 Bunyi |
| `MF:180:2` | Servo maju 180° sebanyak 2 kali | ⚙️ Gerak servo |
| `TR` | Tampilkan suhu di LCD | 🌡️ Baca suhu |
| `HR` | Tampilkan kelembaban di LCD | 💧 Baca kelembaban |
| `D:Hello World!` | Tampilkan teks di LCD | 🖥️ Pesan di layar |

---

## ⚠️ Catatan Penting

- Pastikan **pin DHT11 tidak sama dengan pin LED**.
- Gunakan **power supply eksternal 5V** jika servo dan LCD menyala bersamaan.
- Pastikan alamat I2C LCD (`0x27` atau `0x3F`) sesuai modul kamu.
- Tambahkan resistor pada LED untuk mencegah kerusakan.

---

## 🔋 Skema Power (Sederhana)

