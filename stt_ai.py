"""
stt_ai.py - Pure AI Command Processor (No Hardcoded If-Else)

AI akan memahami perintah natural language dan menghasilkan JSON command
untuk robot. AI dilatih dengan few-shot learning untuk memahami konteks.

Flow:
voice_robot.py (STT) → stt_ai.py (Pure AI) → robot.ino (Hardware)
"""

from transformers import pipeline
import serial
import time
import json
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

ARDUINO_PORT = 'COM3'  # Ganti sesuai port Arduino
BAUD_RATE = 9600

# ============================================================================
# 1. LOAD AI MODEL (GPT-2 untuk Natural Language Understanding)
# ============================================================================

print("="*60)
print("PURE AI COMMAND PROCESSOR - NO HARDCODED RULES")
print("="*60)

print("\nLoading AI Model (GPT-2)...")
try:
    # Gunakan GPT-2 yang lebih besar untuk better understanding
    ai_pipe = pipeline(
        "text-generation", 
        model="gpt2",  # Lebih pintar dari distilgpt2
        max_new_tokens=150,
        temperature=0.3,  # Lower = more deterministic
        top_p=0.9
    )
    print("AI Model loaded!")
except Exception as e:
    print(f"Error loading AI: {e}")
    exit(1)

# ============================================================================
# 2. ARDUINO CONNECTION
# ============================================================================

print(f"\nConnecting to Arduino at {ARDUINO_PORT}...")
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)
    time.sleep(3)
    print("Arduino connected!")
    
    if arduino.in_waiting > 0:
        response = arduino.readline().decode().strip()
        print(f"Arduino: {response}")
except Exception as e:
    print(f"Arduino not connected: {e}")
    print("Running in SIMULATION mode")
    arduino = None

print("\n" + "="*60)
print("AI BRAIN READY - Using Pure Neural Processing")
print("="*60 + "\n")

# ============================================================================
# 3. AI PROMPT ENGINEERING (Few-Shot Learning)
# ============================================================================

def create_ai_prompt(user_text):
    """
    Create AI prompt dengan few-shot examples untuk train AI memahami commands
    """
    
    prompt = f"""You are a robot command interpreter AI. Convert natural language to JSON commands.

ROBOT CAPABILITIES:
- LED Control: pins 8,9,10,11,13 with duration support
- Speaker/Buzzer: frequency (Hz) and duration control
- Servo Motor: clockwise rotation, 360° per command, can repeat
- Temperature Sensor: read current temperature
- Humidity Sensor: read humidity level
- LCD Display: show custom messages

EXAMPLES: