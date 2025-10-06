# Voice Control Robot with AI

A voice-controlled robot that uses AI for natural language processing to control various hardware components.

## Features
- Speech-to-Text using Whisper
- Natural language command processing
- Hardware control via Arduino
- Supports multiple input methods

## Hardware Requirements
- Arduino board (Uno, Mega, etc.)
- LED lights
- Servo motor
- LCD display (I2C)
- DHT11 temperature/humidity sensor
- Speaker/buzzer

## Setup
1. Upload `robot.ino` to your Arduino board
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run `python voice_robot.py`

## Usage
1. Speak your command when prompted
2. The system will process your voice and send commands to the Arduino
3. The robot will execute the corresponding actions

## Project Structure
- `voice_robot.py` - Main voice recognition script
- `stt_ai.py` - AI command processor
- `robot.ino` - Arduino firmware
- `requirements.txt` - Python dependencies
