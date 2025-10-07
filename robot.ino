#include <Servo.h>
#include <LCD_I2C.h>
#include <DFRobot_DHT11.h>
#include <Wire.h>

// === Objects ===
Servo myServo;
LCD_I2C lcd(0x27, 16, 2);
DFRobot_DHT11 DHT;

// === Variables ===
String inputString = "";
int potVal = 0;

void setup() {
  Serial.begin(9600);
  
  // LED Setup - sesuai PANDUAN.md
  pinMode(13, OUTPUT);  // LED 1 - Merah
  pinMode(11, OUTPUT);  // LED 2 - Kuning
  pinMode(10, OUTPUT);  // LED 3 - Hijau
  pinMode(9, OUTPUT);   // LED 4 - Biru
  pinMode(8, OUTPUT);   // LED 5 - Putih
  
  // Buzzer Setup
  pinMode(6, OUTPUT);   // Buzzer/Speaker
  
  // Servo Setup - dipindah ke pin 7
  myServo.attach(7);    // Pin 7 untuk servo
  myServo.write(90);   // Posisi netral
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

void loop() {
  // Baca potensio untuk kontrol servo manual (opsional)
  potVal = analogRead(A0);
  potVal = map(potVal, 0, 1023, 0, 180);
  
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("L")) {
    handleLED(cmd);
  }
  else if (cmd.startsWith("S")) {
    handleSpeaker(cmd);
  }
  else if (cmd.startsWith("M")) {
    handleServo(cmd);
  }
  else if (cmd.startsWith("TR")) {
    handleTemperature();
  }
  else if (cmd.startsWith("HR")) {
    handleHumidity();
  }
  else if (cmd.startsWith("D:")) {
    handleLCD(cmd);
  }
  else {
    Serial.println("ERROR: Unknown command");
  }
}

// ============================================================================
// LED HANDLER dengan DURATION SUPPORT
// ============================================================================

void handleLED(String cmd) {
  // Format: L13:1:5 (LED pin 13, ON, 5 detik)
  //         LA:2:3 (ALL LEDs, BLINK, 3 detik)
  
  int colon1 = cmd.indexOf(':');
  int colon2 = cmd.indexOf(':', colon1 + 1);
  
  String pinStr = cmd.substring(1, colon1);
  int state = cmd.substring(colon1 + 1, colon2).toInt();
  int duration = 0;
  
  if (colon2 != -1) {
    duration = cmd.substring(colon2 + 1).toInt();
  }
  
  // ALL LEDs
  if (pinStr == "A") {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("All LEDs ");
    lcd.print(state == 1 ? "ON" : state == 2 ? "BLINK" : "OFF");
    
    if (state == 0) {
      digitalWrite(13, LOW);
      digitalWrite(11, LOW);
      digitalWrite(10, LOW);
      digitalWrite(9, LOW);
      digitalWrite(8, LOW);
    } 
    else if (state == 1) {
      digitalWrite(13, HIGH);
      digitalWrite(11, HIGH);
      digitalWrite(10, HIGH);
      digitalWrite(9, HIGH);
      digitalWrite(8, HIGH);
      
      if (duration > 0) {
        delay(duration * 1000);
        digitalWrite(13, LOW);
        digitalWrite(11, LOW);
        digitalWrite(10, LOW);
        digitalWrite(9, LOW);
        digitalWrite(8, LOW);
      }
    } 
    else if (state == 2) {
      // Blink all
      int times = duration > 0 ? duration * 2 : 10;
      for (int i = 0; i < times; i++) {
        digitalWrite(13, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(9, HIGH);
        digitalWrite(8, HIGH);
        delay(250);
        digitalWrite(13, LOW);
        digitalWrite(11, LOW);
        digitalWrite(10, LOW);
        digitalWrite(9, LOW);
        digitalWrite(8, LOW);
        delay(250);
      }
    }
    
    Serial.println("OK: All LEDs controlled");
    lcd.clear();
    return;
  }
  
  // Single LED
  int pin = pinStr.toInt();
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("LED Pin ");
  lcd.print(pin);
  lcd.setCursor(0, 1);
  lcd.print(state == 1 ? "ON" : state == 2 ? "BLINK" : "OFF");
  
  if (duration > 0) {
    lcd.print(" ");
    lcd.print(duration);
    lcd.print("s");
  }
  
  if (state == 0) {
    digitalWrite(pin, LOW);
  } 
  else if (state == 1) {
    digitalWrite(pin, HIGH);
    if (duration > 0) {
      delay(duration * 1000);
      digitalWrite(pin, LOW);
    }
  } 
  else if (state == 2) {
    // Blink
    int times = duration > 0 ? duration * 2 : 10;
    for (int i = 0; i < times; i++) {
      digitalWrite(pin, HIGH);
      delay(250);
      digitalWrite(pin, LOW);
      delay(250);
    }
  }
  
  Serial.print("OK: LED ");
  Serial.print(pin);
  Serial.print(" ");
  Serial.println(state == 1 ? "ON" : state == 2 ? "BLINK" : "OFF");
  
  delay(500);
  lcd.clear();
}

// ============================================================================
// SPEAKER HANDLER
// ============================================================================

void handleSpeaker(String cmd) {
  // Format: S500:2 (500Hz selama 2 detik) or S500:1;S1000:1 (multiple tones)
  
  // Split multiple commands if any
  int cmdCount = 0;
  int lastSemicolon = -1;
  
  do {
    int nextSemicolon = cmd.indexOf(';', lastSemicolon + 1);
    String singleCmd;
    
    if (nextSemicolon == -1) {
      singleCmd = cmd.substring(lastSemicolon + 1);
    } else {
      singleCmd = cmd.substring(lastSemicolon + 1, nextSemicolon);
    }
    
    // Process single command
    if (singleCmd.length() > 0 && singleCmd[0] == 'S') {
      int colonPos = singleCmd.indexOf(':');
      if (colonPos != -1) {
        int frequency = singleCmd.substring(1, colonPos).toInt();
        int duration = singleCmd.substring(colonPos + 1).toInt();
        
        // Only update display for the first command
        if (cmdCount == 0) {
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Playing Sound");
          lcd.setCursor(0, 1);
          lcd.print(frequency);
          lcd.print("Hz ");
          lcd.print(duration);
          lcd.print("s");
        }
        
        // Play the tone
        if (frequency > 0) {
          tone(6, frequency, duration * 1000);  // Buzzer on pin 6
          delay(duration * 1000);
          noTone(6);
        } else {
          noTone(6);  // Turn off sound if frequency is 0
        }
        
        Serial.print("Playing: ");
        Serial.print(frequency);
        Serial.print("Hz for ");
        Serial.print(duration);
        Serial.println("s");
        
        cmdCount++;
      }
    }
    
    lastSemicolon = nextSemicolon;
  } while (lastSemicolon != -1);
  
  if (cmdCount > 0) {
    lcd.clear();
  }
}
void handleServo(String cmd) {
  // Format: MF:360:4 (Forward 360° × 4 kali)
  //         MB:180:1 (Backward 180° × 1 kali)
  
  int colon1 = cmd.indexOf(':');
  int colon2 = cmd.indexOf(':', colon1 + 1);
  
  char direction = cmd.charAt(1);
  int degrees = cmd.substring(colon1 + 1, colon2).toInt();
  int repeat = cmd.substring(colon2 + 1).toInt();
  
  String dirText = (direction == 'F') ? "MAJU" : "MUNDUR";
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Servo: ");
  lcd.print(dirText);
  lcd.setCursor(0, 1);
  lcd.print(degrees);
  lcd.print("deg x");
  lcd.print(repeat);
  
  Serial.print("OK: Servo ");
  Serial.print(dirText);
  Serial.print(" ");
  Serial.print(degrees);
  Serial.print(" deg x");
  Serial.print(repeat);
  Serial.println(" times");
  
  // Execute servo movement dengan repeat
  for (int i = 0; i < repeat; i++) {
    lcd.setCursor(13, 1);
    lcd.print(i + 1);
    lcd.print("/");
    lcd.print(repeat);
    
    if (direction == 'F') {
      // Clockwise (Maju)
      rotateServo(true, degrees);
    } else {
      // Counter-clockwise (Mundur)
      rotateServo(false, degrees);
    }
    
    delay(500);  // Jeda antar repeat
  }
  
  delay(500);
  lcd.clear();
}

void rotateServo(bool clockwise, int degrees) {
  // Servo continuous rotation
  // 0° = CCW, 90° = Stop, 180° = CW
  
  int speed = clockwise ? 180 : 0;
  myServo.write(speed);
  
  // Estimasi waktu rotasi (sesuaikan dengan servo kamu)
  // Asumsi: 60 RPM = 360°/detik
  int duration = (degrees * 1000) / 360;
  delay(duration);
  
  // Stop
  myServo.write(90);
}

// ============================================================================
// TEMPERATURE HANDLER
// ============================================================================

void handleTemperature() {
  DHT.read(11);  // DHT11 di pin 11
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Mengukur Suhu...");
  delay(500);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Suhu: ");
  lcd.print(DHT.temperature);
  lcd.print("C");
  lcd.setCursor(0, 1);
  lcd.print("Kelembaban:");
  lcd.print(DHT.humidity);
  lcd.print("%");
  
  Serial.print("TEMP: ");
  Serial.print(DHT.temperature);
  Serial.println(" C");
  
  // Auto control LED berdasarkan suhu
  if (DHT.temperature > 28) {
    digitalWrite(10, HIGH);
    digitalWrite(8, LOW);
  } else {
    digitalWrite(10, LOW);
    digitalWrite(8, HIGH);
  }
  
  delay(3000);
  lcd.clear();
}

// ============================================================================
// HUMIDITY HANDLER
// ============================================================================

void handleHumidity() {
  DHT.read(11);  // DHT11 di pin 11
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Kelembaban:");
  lcd.setCursor(0, 1);
  lcd.print(DHT.humidity);
  lcd.print(" %");
  
  Serial.print("HUMIDITY: ");
  Serial.print(DHT.humidity);
  Serial.println(" %");
  
  delay(3000);
  lcd.clear();
}

// ============================================================================
// LCD HANDLER
// ============================================================================

void handleLCD(String cmd) {
  // Format: D:halo dunia
  String message = cmd.substring(2);
  message.trim();
  
  lcd.clear();
  lcd.setCursor(0, 0);
  
  // Split message jika lebih dari 16 karakter
  if (message.length() <= 16) {
    lcd.print(message);
  } else {
    lcd.print(message.substring(0, 16));
    lcd.setCursor(0, 1);
    lcd.print(message.substring(16));
  }
  
  Serial.print("OK: LCD Display: ");
  Serial.println(message);
  
  delay(3000);
  lcd.clear();
}