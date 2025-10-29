#include <Servo.h>
#include <LCD_I2C.h>
#include <DFRobot_DHT11.h>
#include <Wire.h>

// ============================================================
// CONFIGURATION
// ============================================================

// Pin Definitions
#define LED_RED    13
#define LED_YELLOW 12
#define LED_GREEN  11
#define LED_BLUE   10
#define LED_WHITE  9
#define BUZZER     8
#define SERVO_PIN  7
#define POT_PIN    A0
#define DHT_PIN    2

// Timing Constants
#define BLINK_DELAY 250
#define SHORT_DELAY 500
#define LONG_DELAY 1000
#define LCD_DISPLAY_TIME 3000

// Limits
#define MAX_INPUT_LENGTH 100
#define MIN_LED_PIN 9
#define MAX_LED_PIN 13
#define MIN_FREQUENCY 20
#define MAX_FREQUENCY 20000
#define MIN_TEMP -40
#define MAX_TEMP 80
#define MIN_HUMIDITY 0
#define MAX_HUMIDITY 100

// ============================================================
// GLOBAL OBJECTS
// ============================================================

Servo myServo;
LCD_I2C lcd(0x27, 16, 2);
DFRobot_DHT11 DHT;

// ============================================================
// GLOBAL VARIABLES
// ============================================================

char inputBuffer[MAX_INPUT_LENGTH + 1];
uint8_t inputIndex = 0;
bool commandReady = false;

// Non-blocking timing
unsigned long lastLCDUpdate = 0;
bool lcdNeedsClear = false;

// Error tracking
uint8_t errorCount = 0;
#define MAX_ERRORS 10

// ============================================================
// SETUP
// ============================================================

void setup() {
  // Serial Communication
  Serial.begin(9600);
  while (!Serial && millis() < 3000);  // Wait up to 3 seconds
  
  // LED Setup
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_WHITE, OUTPUT);
  
  // Initialize all LEDs OFF
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_WHITE, LOW);
  
  // Buzzer Setup
  pinMode(BUZZER, OUTPUT);
  noTone(BUZZER);
  
  // Servo Setup
  myServo.attach(SERVO_PIN);
  myServo.write(90);  // Neutral position
  
  // LCD Setup
  lcd.begin();
  lcd.display();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("AI Robot v2.0");
  lcd.setCursor(0, 1);
  lcd.print("Ready!");
  
  // Startup tone
  tone(BUZZER, 1000, 100);
  delay(150);
  tone(BUZZER, 1500, 100);
  
  delay(2000);
  lcd.clear();
  
  Serial.println("READY");
  Serial.flush();
}

// ============================================================
// MAIN LOOP
// ============================================================

void loop() {
  // Handle LCD auto-clear
  if (lcdNeedsClear && (millis() - lastLCDUpdate > LCD_DISPLAY_TIME)) {
    lcd.clear();
    lcdNeedsClear = false;
  }
  
  // Process commands
  if (commandReady) {
    processCommand(inputBuffer);
    
    // Clear buffer
    inputIndex = 0;
    inputBuffer[0] = '\0';
    commandReady = false;
  }
  
  // Check for errors
  if (errorCount >= MAX_ERRORS) {
    handleCriticalError();
  }
}

// ============================================================
// SERIAL EVENT (Non-blocking input)
// ============================================================

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputIndex > 0) {
        inputBuffer[inputIndex] = '\0';
        commandReady = true;
      }
    } 
    else if (inputIndex < MAX_INPUT_LENGTH) {
      inputBuffer[inputIndex++] = inChar;
    } 
    else {
      // Buffer overflow - clear and report error
      inputIndex = 0;
      Serial.println("ERROR: Command too long");
      errorCount++;
    }
  }
}

// ============================================================
// COMMAND PROCESSING
// ============================================================

void processCommand(char* cmd) {
  // Trim whitespace
  while (*cmd == ' ') cmd++;
  
  if (strlen(cmd) == 0) {
    return;
  }
  
  // Route command
  switch (cmd[0]) {
    case 'L':  // LED control
      handleLED(cmd);
      break;
    case 'S':  // Speaker/Sound
      handleSpeaker(cmd);
      break;
    case 'M':  // Motor/Servo
      handleServo(cmd);
      break;
    case 'T':  // Temperature
      if (cmd[1] == 'R') handleTemperature();
      else sendError("Unknown command");
      break;
    case 'H':  // Humidity
      if (cmd[1] == 'R') handleHumidity();
      else sendError("Unknown command");
      break;
    case 'D':  // Display (LCD)
      handleLCD(cmd);
      break;
    case 'P':  // Ping (heartbeat)
      Serial.println("PONG");
      break;
    default:
      sendError("Unknown command");
      break;
  }
}

// ============================================================
// LED HANDLER
// ============================================================

void handleLED(char* cmd) {
  // Format: L13:1:5 (pin 13, ON, 5 seconds)
  //         LA:2:3  (ALL, BLINK, 3 seconds)
  
  char* token = strtok(cmd + 1, ":");
  if (!token) {
    sendError("Invalid LED command format");
    return;
  }
  
  // Parse pin/mode
  bool allLEDs = (token[0] == 'A');
  int pin = allLEDs ? 0 : atoi(token);
  
  // Validate pin
  if (!allLEDs && (pin < MIN_LED_PIN || pin > MAX_LED_PIN)) {
    sendError("Invalid LED pin");
    return;
  }
  
  // Parse state
  token = strtok(NULL, ":");
  if (!token) {
    sendError("Missing LED state");
    return;
  }
  int state = atoi(token);
  
  // Parse duration (optional)
  token = strtok(NULL, ":");
  int duration = token ? atoi(token) : 0;
  
  // Update LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(allLEDs ? "All LEDs" : "LED ");
  if (!allLEDs) lcd.print(pin);
  lcd.setCursor(0, 1);
  lcd.print(state == 0 ? "OFF" : state == 1 ? "ON" : "BLINK");
  
  lastLCDUpdate = millis();
  lcdNeedsClear = true;
  
  // Execute command
  if (allLEDs) {
    controlAllLEDs(state, duration);
  } else {
    controlSingleLED(pin, state, duration);
  }
  
  Serial.print("OK: LED ");
  Serial.print(allLEDs ? "ALL" : String(pin));
  Serial.print(" ");
  Serial.println(state == 0 ? "OFF" : state == 1 ? "ON" : "BLINK");
}

void controlSingleLED(int pin, int state, int duration) {
  if (state == 0) {
    // OFF
    digitalWrite(pin, LOW);
  } 
  else if (state == 1) {
    // ON
    digitalWrite(pin, HIGH);
    if (duration > 0) {
      delay(duration * 1000);
      digitalWrite(pin, LOW);
    }
  } 
  else if (state == 2) {
    // BLINK
    int times = duration > 0 ? duration * 2 : 10;
    for (int i = 0; i < times; i++) {
      digitalWrite(pin, HIGH);
      delay(BLINK_DELAY);
      digitalWrite(pin, LOW);
      delay(BLINK_DELAY);
    }
  }
}

void controlAllLEDs(int state, int duration) {
  int pins[] = {LED_RED, LED_YELLOW, LED_GREEN, LED_BLUE, LED_WHITE};
  
  if (state == 0) {
    // OFF
    for (int i = 0; i < 5; i++) {
      digitalWrite(pins[i], LOW);
    }
  } 
  else if (state == 1) {
    // ON
    for (int i = 0; i < 5; i++) {
      digitalWrite(pins[i], HIGH);
    }
    if (duration > 0) {
      delay(duration * 1000);
      for (int i = 0; i < 5; i++) {
        digitalWrite(pins[i], LOW);
      }
    }
  } 
  else if (state == 2) {
    // BLINK
    int times = duration > 0 ? duration * 2 : 10;
    for (int i = 0; i < times; i++) {
      for (int j = 0; j < 5; j++) {
        digitalWrite(pins[j], HIGH);
      }
      delay(BLINK_DELAY);
      for (int j = 0; j < 5; j++) {
        digitalWrite(pins[j], LOW);
      }
      delay(BLINK_DELAY);
    }
  }
}

// ============================================================
// SPEAKER HANDLER
// ============================================================

void handleSpeaker(char* cmd) {
  // Format: S1000:2 (1000Hz for 2 seconds)
  
  char cmdCopy[MAX_INPUT_LENGTH];
  strncpy(cmdCopy, cmd, MAX_INPUT_LENGTH);
  
  char* token = strtok(cmdCopy + 1, ";");
  int toneCount = 0;
  
  while (token != NULL && toneCount < 10) {
    char* freqStr = strtok(token, ":");
    char* durStr = strtok(NULL, ":");
    
    if (freqStr && durStr) {
      int frequency = atoi(freqStr);
      int duration = atoi(durStr);
      
      // Validate frequency
      if (frequency < MIN_FREQUENCY) frequency = MIN_FREQUENCY;
      if (frequency > MAX_FREQUENCY) frequency = MAX_FREQUENCY;
      
      // Validate duration
      if (duration > 10) duration = 10;  // Max 10 seconds
      
      if (toneCount == 0) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Playing Sound");
        lcd.setCursor(0, 1);
        lcd.print(frequency);
        lcd.print("Hz ");
        lcd.print(duration);
        lcd.print("s");
        
        lastLCDUpdate = millis();
        lcdNeedsClear = true;
      }
      
      tone(BUZZER, frequency, duration * 1000);
      delay(duration * 1000);
      noTone(BUZZER);
      
      toneCount++;
    }
    
    token = strtok(NULL, ";");
  }
  
  if (toneCount > 0) {
    Serial.print("OK: Played ");
    Serial.print(toneCount);
    Serial.println(" tones");
  } else {
    sendError("Invalid speaker command");
  }
}

// ============================================================
// SERVO HANDLER
// ============================================================

void handleServo(char* cmd) {
  // Format: MF:360:4 (Forward 360° × 4 times)
  
  char direction = cmd[1];
  if (direction != 'F' && direction != 'B' && direction != 'L' && 
      direction != 'R' && direction != 'S') {
    sendError("Invalid servo direction");
    return;
  }
  
  char* token = strtok(cmd + 3, ":");
  if (!token) {
    sendError("Invalid servo command");
    return;
  }
  
  int degrees = atoi(token);
  token = strtok(NULL, ":");
  int repeat = token ? atoi(token) : 1;
  
  // Validate
  if (degrees < 0 || degrees > 360) degrees = 90;
  if (repeat < 0 || repeat > 10) repeat = 1;
  
  // Update LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Servo: ");
  lcd.print(direction == 'F' ? "FWD" : direction == 'B' ? "BACK" : 
           direction == 'L' ? "LEFT" : direction == 'R' ? "RIGHT" : "STOP");
  
  lastLCDUpdate = millis();
  lcdNeedsClear = true;
  
  // Execute
  if (direction == 'S') {
    // Stop
    myServo.write(90);
    Serial.println("OK: Servo STOP");
    return;
  }
  
  for (int i = 0; i < repeat; i++) {
    lcd.setCursor(0, 1);
    lcd.print(i + 1);
    lcd.print("/");
    lcd.print(repeat);
    
    if (direction == 'F') {
      myServo.write(180);
    } else if (direction == 'B') {
      myServo.write(0);
    } else if (direction == 'L') {
      myServo.write(45);
    } else if (direction == 'R') {
      myServo.write(135);
    }
    
    delay((degrees * 1000) / 360);
    myServo.write(90);  // Stop
    delay(SHORT_DELAY);
  }
  
  Serial.print("OK: Servo ");
  Serial.print(direction);
  Serial.print(" x");
  Serial.println(repeat);
}

// ============================================================
// TEMPERATURE HANDLER
// ============================================================

void handleTemperature() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Reading Temp...");
  
  int result = DHT.read(DHT_PIN);
  
  if (result != 0) {
    sendError("DHT sensor failed");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error!");
    lastLCDUpdate = millis();
    lcdNeedsClear = true;
    return;
  }
  
  float temp = DHT.temperature;
  
  // Validate reading
  if (temp < MIN_TEMP || temp > MAX_TEMP) {
    sendError("Invalid temperature");
    return;
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temp, 1);
  lcd.print("C");
  lcd.setCursor(0, 1);
  lcd.print("Humid: ");
  lcd.print(DHT.humidity, 1);
  lcd.print("%");
  
  lastLCDUpdate = millis();
  lcdNeedsClear = true;
  
  Serial.print("TEMP:");
  Serial.println(temp, 1);
  
  // Auto LED control
  if (temp > 28) {
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_BLUE, LOW);
  } else if (temp < 20) {
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_BLUE, HIGH);
  }
}

// ============================================================
// HUMIDITY HANDLER
// ============================================================

void handleHumidity() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Reading Humid...");
  
  int result = DHT.read(DHT_PIN);
  
  if (result != 0) {
    sendError("DHT sensor failed");
    return;
  }
  
  float humidity = DHT.humidity;
  
  // Validate
  if (humidity < MIN_HUMIDITY || humidity > MAX_HUMIDITY) {
    sendError("Invalid humidity");
    return;
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Humidity:");
  lcd.setCursor(0, 1);
  lcd.print(humidity, 1);
  lcd.print(" %");
  
  lastLCDUpdate = millis();
  lcdNeedsClear = true;
  
  Serial.print("HUMID:");
  Serial.println(humidity, 1);
}

// ============================================================
// LCD HANDLER
// ============================================================

void handleLCD(char* cmd) {
  // Format: D:Hello World
  
  char* message = cmd + 2;
  
  lcd.clear();
  lcd.setCursor(0, 0);
  
  int len = strlen(message);
  if (len <= 16) {
    lcd.print(message);
  } else {
    // Split into two lines
    for (int i = 0; i < 16 && i < len; i++) {
      lcd.print(message[i]);
    }
    if (len > 16) {
      lcd.setCursor(0, 1);
      for (int i = 16; i < 32 && i < len; i++) {
        lcd.print(message[i]);
      }
    }
  }
  
  lastLCDUpdate = millis();
  lcdNeedsClear = true;
  
  Serial.print("OK: LCD ");
  Serial.println(message);
}

// ============================================================
// ERROR HANDLING
// ============================================================

void sendError(const char* message) {
  Serial.print("ERROR: ");
  Serial.println(message);
  errorCount++;
}

void handleCriticalError() {
  // Critical error - reset everything
  Serial.println("CRITICAL: Too many errors, resetting...");
  
  // Turn off all outputs
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_WHITE, LOW);
  noTone(BUZZER);
  myServo.write(90);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SYSTEM ERROR!");
  lcd.setCursor(0, 1);
  lcd.print("Resetting...");
  
  delay(3000);
  
  // Software reset
  asm volatile ("  jmp 0");
}