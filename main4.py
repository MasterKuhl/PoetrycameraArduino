import os
import time
import openai
import serial
import picamera
from dotenv import load_dotenv

# Laden des OpenAI API-Schlüssels aus nano.env
load_dotenv("nano.env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Bilddateipfad
IMAGE_PATH = "/home/pi/image.jpg"

# Arduino serieller Port (USB-Verbindung)
ARDUINO_PORT = "/dev/ttyACM0"  # /dev/ttyUSB0 oder /dev/ttyACM0 prüfen
BAUD_RATE = 9600

def capture_image():
    """Nimmt ein Bild mit der Raspberry Pi Kamera auf."""
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.capture(IMAGE_PATH)
    print("Bild aufgenommen.")

def image_to_poem():
    """Sendet das Bild an OpenAI API und erhält ein Gedicht zurück."""
    with open(IMAGE_PATH, "rb") as image_file:
        image_data = image_file.read()

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "Du bist ein kreativer Dichter. Schreibe ein Gedicht basierend auf dem Bild."},
            {"role": "user", "content": "Erzeuge ein Gedicht, das dieses Bild beschreibt."}
        ],
        max_tokens=150
    )

    poem = response["choices"][0]["message"]["content"]
    print("Generiertes Gedicht:\n", poem)
    return poem

def send_to_arduino(poem):
    """Sendet das Gedicht über die serielle USB-Schnittstelle an den Arduino."""
    try:
        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1) as arduino:
            time.sleep(2)  # Warten, bis die Verbindung stabil ist
            arduino.write(poem.encode('utf-8'))
            print("Gedicht an Arduino gesendet.")
    except Exception as e:
        print("Fehler beim Senden an Arduino:", e)

# Hauptablauf
capture_image()
poem = image_to_poem()
send_to_arduino(poem)
