import time
import requests
import serial
import os
from picamera import PiCamera
from openai import OpenAI
from dotenv import load_dotenv

# Lade API-Schlüssel aus nano.env
load_dotenv("nano.env")
oai_api_key = os.getenv("OPENAI_API_KEY")

# Konfiguration der Kamera
camera = PiCamera()
camera.resolution = (1024, 768)

# Konfiguration der seriellen Verbindung zum Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flush()

def take_photo():
    filename = "/home/pi/photo.jpg"
    camera.capture(filename)
    print("Foto aufgenommen.")
    return filename

def send_to_openai(image_path):
    headers = {"Authorization": f"Bearer {oai_api_key}"}
    with open(image_path, "rb") as file:
        files = {"file": file}
        data = {"model": "gpt-4-vision-preview", "prompt": "Erstelle ein kurzes Gedicht basierend auf diesem Bild.", "max_tokens": 100}
        
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        poem = response.json().get("choices", [{}])[0].get("text", "Fehler beim Generieren des Gedichts.")
        print("Gedicht erhalten:", poem)
        return poem
    else:
        print("Fehler bei der API-Anfrage:", response.text)
        return "Fehler beim Abrufen des Gedichts."

def send_to_arduino(text):
    ser.write((text + "\n").encode('utf-8'))
    print("Gedicht an Arduino gesendet: ", text)

if __name__ == "__main__":
    photo_path = take_photo()
    poem = send_to_openai(photo_path)
    send_to_arduino(poem)
