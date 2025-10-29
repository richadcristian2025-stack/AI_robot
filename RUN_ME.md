# 🤖 VOICE CONTROLLED ROBOT AI - COMPLETE GUIDE

## 📋 SYSTEM COMPONENTS

### 1. **ml_ai.py** - Machine Learning Model
- Processes voice commands using ML
- Trained on Indonesian & English commands
- Converts text to Arduino commands

### 2. **web_interface.py** - Web Server (Port 4141)
- Flask web server
- Whisper AI for speech-to-text
- Handles audio processing
- Sends commands to Arduino

### 3. **robot.ino** - Arduino Firmware
- Controls LEDs, motors, sensors
- Receives serial commands
- Executes hardware actions

### 4. **templates/index.html** - Web Interface
- Voice recording interface
- Command history
- Real-time status

---

## 🚀 HOW TO RUN

### STEP 1: Upload Arduino Code
```
1. Open Arduino IDE
2. Open robot.ino
3. Select your board (Arduino Uno/Mega)
4. Select COM port
5. Click Upload
6. Wait for "Done uploading"
```

### STEP 2: Start Web Server
```bash
python web_interface.py
```

**Server will start on:**
- **URL:** http://localhost:4141
- **Port:** 4141

### STEP 3: Open Browser
```
Go to: http://localhost:4141
```

### STEP 4: Use Voice Commands
```
1. Click microphone button
2. Say command (e.g., "turn on the light")
3. Click again to stop recording
4. See result on screen
```

---

## 🎤 VOICE COMMANDS

### English Commands
- **"turn on the light"** → LED ON
- **"turn off the light"** → LED OFF
- **"forward"** → Move forward
- **"backward"** → Move backward
- **"left"** → Turn left
- **"right"** → Turn right
- **"stop"** → Stop all
- **"temperature"** → Read temp
- **"alarm"** → Sound alarm

### Indonesian Commands
- **"nyalakan lampu"** → LED ON
- **"matikan lampu"** → LED OFF
- **"maju"** → Move forward
- **"mundur"** → Move backward
- **"kiri"** → Turn left
- **"kanan"** → Turn right
- **"berhenti"** → Stop all
- **"suhu"** → Read temp

---

## 🔌 PORTS & CONNECTIONS

### Web Server
- **Port:** 4141
- **Access:** http://localhost:4141
- **API Endpoints:**
  - `/api/process_audio` - Process voice
  - `/api/status` - System status
  - `/api/history` - Command history
  - `/api/check-connection` - Arduino status

### Arduino Serial
- **Baud Rate:** 9600
- **Port:** Auto-detected (COM3, COM4, etc.)
- **Timeout:** 2 seconds

### LED Pins
- Pin 13 - Red LED
- Pin 12 - Yellow LED
- Pin 11 - Green LED
- Pin 10 - Blue LED
- Pin 9 - White LED

---

## 📦 REQUIRED PACKAGES

Install with:
```bash
pip install flask flask-cors torch transformers numpy scikit-learn pyserial
```

---

## ⚙️ SYSTEM FLOW

```
1. User speaks → Browser captures audio
2. Audio sent → Flask server (port 4141)
3. Whisper AI → Converts speech to text
4. ML Model → Classifies command
5. Arduino command → Sent via serial
6. Arduino → Executes action (LED/motor)
7. Response → Displayed in browser
```

---

## 🐛 TROUBLESHOOTING

### Arduino Not Detected
- Check USB cable
- Verify COM port in Device Manager
- System runs in SIMULATION mode if not found

### Web Server Won't Start
- Check if port 4141 is available
- Kill any process using port 4141:
  ```bash
  netstat -ano | findstr :4141
  taskkill /PID <PID> /F
  ```

### Voice Not Recognized
- Check microphone permissions
- Speak clearly and slowly
- Try both English and Indonesian

### ML Model Error
- Delete `robot_ml_model.pkl`
- Restart server (will retrain)

---

## 📝 QUICK START COMMANDS

```bash
# 1. Upload Arduino code first
# 2. Then run:
python web_interface.py

# 3. Open browser:
# http://localhost:4141

# 4. Click mic and say:
# "turn on the light"
```

---

## 🎯 TESTING WITHOUT ARDUINO

The system works in **SIMULATION MODE** if Arduino is not connected:
- All commands are logged to console
- No hardware actions occur
- Perfect for testing voice recognition

---

## 📊 COMMAND FORMAT (Arduino)

| Command | Format | Example |
|---------|--------|---------|
| LED ON | L{pin}:1:0 | L13:1:0 |
| LED OFF | L{pin}:0:0 | L13:0:0 |
| Move | M{dir}:{deg}:{rep} | MF:90:1 |
| Sound | S{freq}:{dur} | S1000:1 |
| Sensor | TR or HR | TR |

---

## ✅ SYSTEM READY CHECKLIST

- [ ] Arduino code uploaded
- [ ] Python packages installed
- [ ] Web server running (port 4141)
- [ ] Browser opened to localhost:4141
- [ ] Microphone permissions granted
- [ ] Arduino connected (or simulation mode)

---

**🎉 YOU'RE READY TO GO!**

Just run: `python web_interface.py` and open http://localhost:4141
