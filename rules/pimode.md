# 📍 PIN MODE CONFIGURATION - Arduino Robot

## DETAIL PIN MODE LENGKAP

### 🔴 OUTPUT PINS - Digital Write
```cpp
pinMode(13, OUTPUT);  // LED_RED - LED Merah
pinMode(12, OUTPUT);  // LED_YELLOW - LED Kuning  
pinMode(11, OUTPUT);  // LED_GREEN - LED Hijau
pinMode(10, OUTPUT);  // LED_BLUE - LED Biru
pinMode(9, OUTPUT);   // LED_WHITE - LED Putih
pinMode(8, OUTPUT);   // BUZZER - Speaker/Buzzer
pinMode(7, OUTPUT);   // SERVO_PIN - Servo Motor (via myServo.attach())
```

### 🟢 INPUT PINS - Digital Read
```cpp
pinMode(2, INPUT);    // DHT_PIN - DHT11 Sensor (Suhu & Kelembaban)
                      // Note: Library DFRobot_DHT11 akan mengatur ini otomatis
```

### 🟡 INPUT PINS - Analog Read
```cpp
pinMode(A0, INPUT);   // POT_PIN - Potentiometer
                      // Note: Analog pins default INPUT, tidak wajib di-set
```

### 🔵 I2C PINS - Auto-configured (Wire.h)
```cpp
// pinMode(A4, OUTPUT/INPUT); // SDA - LCD Data (diatur otomatis oleh Wire.h)
// pinMode(A5, OUTPUT);       // SCL - LCD Clock (diatur otomatis oleh Wire.h)
```

### ⚪ COMMUNICATION PINS - Hardware Serial
```cpp
// pinMode(0, INPUT);   // RX - Serial Receive (diatur otomatis oleh Serial.begin())
// pinMode(1, OUTPUT);  // TX - Serial Transmit (diatur otomatis oleh Serial.begin())
```

---

## 📋 TABEL LENGKAP PIN MODE

| Pin  | Nama         | pinMode()    | Fungsi              | Catatan                          |
|------|--------------|--------------|---------------------|----------------------------------|
| 0    | RX           | *(auto)*     | Serial Receive      | Diatur oleh `Serial.begin(9600)` |
| 1    | TX           | *(auto)*     | Serial Transmit     | Diatur oleh `Serial.begin(9600)` |
| 2    | DHT_PIN      | `INPUT`      | DHT11 Sensor        | Library mengatur otomatis        |
| 7    | SERVO_PIN    | `OUTPUT`     | Servo Motor         | Via `myServo.attach(7)`          |
| 8    | BUZZER       | `OUTPUT`     | Speaker/Buzzer      | `tone()` dan `noTone()`          |
| 9    | LED_WHITE    | `OUTPUT`     | LED Putih           | `digitalWrite()`                 |
| 10   | LED_BLUE     | `OUTPUT`     | LED Biru            | `digitalWrite()`                 |
| 11   | LED_GREEN    | `OUTPUT`     | LED Hijau           | `digitalWrite()`                 |
| 12   | LED_YELLOW   | `OUTPUT`     | LED Kuning          | `digitalWrite()`                 |
| 13   | LED_RED      | `OUTPUT`     | LED Merah           | `digitalWrite()` + Built-in LED  |
| A0   | POT_PIN      | `INPUT`      | Potentiometer       | `analogRead()` (0-1023)          |
| A4   | SDA          | *(auto)*     | I2C Data            | Diatur oleh `Wire.h`             |
| A5   | SCL          | *(auto)*     | I2C Clock           | Diatur oleh `Wire.h`             |

---

## 🔧 KODE SETUP() LENGKAP

```cpp
void setup() {
  Serial.begin(9600);  // Pin 0 (RX) dan Pin 1 (TX) otomatis diatur
  
  // ========================================
  // OUTPUT PINS
  // ========================================
  pinMode(13, OUTPUT);  // LED_RED - LED Merah
  pinMode(12, OUTPUT);  // LED_YELLOW - LED Kuning
  pinMode(11, OUTPUT);  // LED_GREEN - LED Hijau
  pinMode(10, OUTPUT);  // LED_BLUE - LED Biru
  pinMode(9, OUTPUT);   // LED_WHITE - LED Putih
  pinMode(8, OUTPUT);   // BUZZER - Speaker/Buzzer
  
  // ========================================
  // SERVO (OUTPUT via Library)
  // ========================================
  myServo.attach(7);    // SERVO_PIN - Library mengatur pinMode
  myServo.write(90);    // Posisi netral
  
  // ========================================
  // INPUT PINS (Opsional)
  // ========================================
  // pinMode(2, INPUT);    // DHT_PIN - Library akan set otomatis
  // pinMode(A0, INPUT);   // POT_PIN - Analog default INPUT
  
  // ========================================
  // I2C (Auto-configured by Wire.h)
  // ========================================
  lcd.begin();          // Pin A4 (SDA) dan A5 (SCL) otomatis diatur
  lcd.display();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("AI Robot Ready!");
  
  inputString.reserve(100);
  
  delay(1000);
  lcd.clear();
  Serial.println("Arduino Ready!");
}
```

---

## 📊 PIN USAGE SUMMARY

### OUTPUT Pins (7 pins)
- **Digital 7-13**: LEDs (5), Buzzer (1), Servo (1)
- Menggunakan: `digitalWrite()`, `tone()`, `myServo.write()`

### INPUT Pins (2 pins)
- **Digital 2**: DHT11 Sensor
- **Analog A0**: Potentiometer
- Menggunakan: `DHT.read()`, `analogRead()`

### Communication Pins (4 pins)
- **Digital 0-1**: Serial UART (RX/TX)
- **Analog A4-A5**: I2C (SDA/SCL) untuk LCD
- Menggunakan: `Serial`, `Wire`, `lcd`

---

## ⚡ CATATAN PENTING

### 1. Pin yang WAJIB di-set dengan pinMode()
```cpp
pinMode(13, OUTPUT);  // LED_RED
pinMode(12, OUTPUT);  // LED_YELLOW
pinMode(11, OUTPUT);  // LED_GREEN
pinMode(10, OUTPUT);  // LED_BLUE
pinMode(9, OUTPUT);   // LED_WHITE
pinMode(8, OUTPUT);   // BUZZER
```

### 2. Pin yang OPSIONAL (sudah default INPUT)
```cpp
// pinMode(A0, INPUT);  // Analog pins default INPUT
// pinMode(2, INPUT);   // Library akan set
```

### 3. Pin yang OTOMATIS (jangan di-set manual)
```cpp
// Serial.begin(9600);     // Pin 0-1 otomatis
// myServo.attach(7);      // Pin 7 otomatis
// lcd.begin();            // Pin A4-A5 otomatis
```

---

## 🎯 KESIMPULAN

**Total pins digunakan: 13 pins**
- 6 pins OUTPUT manual (LEDs + Buzzer)
- 1 pin OUTPUT via library (Servo)
- 2 pins INPUT (DHT11 + Potentiometer)
- 4 pins komunikasi otomatis (Serial + I2C)

**Yang perlu di-set pinMode() di setup(): 6 pins saja!**

---

## 🔌 WIRING DIAGRAM REFERENCE

```
Arduino Uno
┌─────────────────┐
│  DIGITAL PINS   │
├─────────────────┤
│ 0  - RX (auto)  │ Serial
│ 1  - TX (auto)  │ Serial
│ 2  - DHT11      │ INPUT (auto by library)
│ 7  - Servo      │ OUTPUT (auto by library)
│ 8  - Buzzer     │ OUTPUT
│ 9  - LED White  │ OUTPUT
│ 10 - LED Blue   │ OUTPUT
│ 11 - LED Green  │ OUTPUT
│ 12 - LED Yellow │ OUTPUT
│ 13 - LED Red    │ OUTPUT
├─────────────────┤
│  ANALOG PINS    │
├─────────────────┤
│ A0 - Potensio   │ INPUT (default)
│ A4 - SDA (auto) │ I2C LCD
│ A5 - SCL (auto) │ I2C LCD
└─────────────────┘
```

---

**File:** PIN_MODE_CONFIGURATION.md  
**Project:** AI Robot Arduino  
**Last Updated:** October 2025