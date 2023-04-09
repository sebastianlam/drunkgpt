import os
import openai
import speech_recognition as sr
import pyttsx3

openai.api_key = os.getenv("OPENAI_API_KEY")

r = sr.Recognizer()

# def transcribe():
#     with sr.Microphone() as source:
#         print("Listening...")
#         audio = r.listen(source)
#         print("thinking...")
#     try:
#         return r.recognize_whisper_api(audio, api_key=openai.api_key)
#     except sr.speech_recognition.exceptions.SetupError as e:
#         print(e)
#     except sr.RequestError as e:
#         print("Could not request results from Whisper API")

# result = transcribe()

# print(result)


engine = pyttsx3.init()
voices = engine.getProperty('voices')
voicearr = [vars(voice) for voice in voices]
for voice in voicearr:
    print(voice)
    # engine.setProperty('voice', voice.id)
    # engine.say("Hello World!")
    # engine.runAndWait()
    # engine.stop()