import os
import openai
import speech_recognition as sr

openai.api_key = os.getenv("OPENAI_API_KEY")

r = sr.Recognizer()

def transcribe():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_whisper_api(audio, api_key=openai.api_key)
    except sr.RequestError as e:
        print("Could not request results from Whisper API")

result = transcribe()

print(result)