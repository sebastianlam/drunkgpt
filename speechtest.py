import os
import openai
import speech_recognition as sr

openai.api_key = os.getenv("OPENAI_API_KEY")

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

try:
    print(f"Whisper API thinks you said {r.recognize_whisper_api(audio, api_key=openai.api_key)}")
except sr.RequestError as e:
    print("Could not request results from Whisper API")