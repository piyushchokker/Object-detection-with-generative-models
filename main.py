import speech_recognition as sr
import pyttsx3
import pygame
import pygame.camera
import os
from google import genai
import cv2

from dotenv import load_dotenv, dotenv_values

load_dotenv()

recognizer = sr.Recognizer()

engine = pyttsx3.init()


def check_image_exists(filename="captured_image.jpg"):
    return os.path.exists(filename)

def delete_image(filename="captured_image.jpg"):
    try:
        os.remove(filename)
        print(f"Image '{filename}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"Image '{filename}' does not exist in the current directory.")


def recognize_speech():
    try:
        with sr.Microphone() as source:
            print("Listening for 'hello'...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)

            # Recognize speech
            recognized_text = recognizer.recognize_google(audio)
            print(f"Recognized: {recognized_text}")
            return recognized_text.lower()
    except sr.WaitTimeoutError:
        print("Timeout: No speech detected.")
        return None
    except sr.UnknownValueError:
        print("Error: Could not understand audio.")
        return None

def say_hello():

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not accessible.")
        return

    ret, frame = cap.read()
    if ret:
        cv2.imwrite("captured_image.jpg", frame)
        print("Image captured successfully.")
    else:
        print("Failed to capture image.")

    cap.release()


def vision_ai(arument = None):

    client = genai.Client(api_key = os.getenv("GOOGLE_API_KEY"))

    my_file = client.files.upload(file="captured_image.jpg")

  
    if check_image_exists():
        response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[my_file, arument ],
            )
        
        delete_image()
    

    return response.text

def text_ai(arument = None):

    client = genai.Client(api_key= os.getenv('GOOGLE_API_KEY'))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[f"{arument}"]
    )

    return response.text


def text_to_speech(text):

    engine = pyttsx3.init()


    engine.setProperty("rate", 150)  # Speed of speech
    engine.setProperty("volume", 1.0)


    engine.say(text)

    engine.save_to_file(text, "output.mp3")
    engine.runAndWait()

vision_list=["what is this","use camera","can u detect","what is there"]
speachtext=""
print(speachtext)

def main():
    while True:
        recognized_text = recognize_speech()
        speachtext=recognized_text

        if recognized_text:
            if any(char in recognized_text for char in vision_list):
                say_hello()
                
                input_text = vision_ai(recognized_text)
                text_to_speech(input_text)
                print(f"Text converted to speech: {input_text}")
            
            else:
                input_text = text_ai(recognized_text)
                text_to_speech(input_text)
                print(f"Text converted to speech: {input_text}")

if __name__ == "__main__":
    main()
