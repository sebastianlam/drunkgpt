import os
import json
import sys
import datetime
import openai
import pyttsx3
import speech_recognition as sr

# Constants and configurations
LOG_FILE = "log.json"
PERSONAS_FILE = "personas.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = "gpt-3.5-turbo"

# Initialize Text to Speech engine
engine = pyttsx3.init()
engine.setProperty('rate', engine.getProperty('rate') - 30)

# Initialize Speech Recognition
recognizer = sr.Recognizer()

# Load personas from file
with open(PERSONAS_FILE, 'r') as f:
    personas = json.load(f)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


def current_time_str():
    return str(datetime.datetime.utcnow())


def speech_prompt():
    choice = input("Would you like to talk? (y/n): ")
    return choice.lower() == "y"


def transcribe():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        print("thinking...")
        return recognizer.recognize_whisper_api(audio, api_key=openai.api_key)
    except sr.RequestError:
        print("Could not request results from Whisper API")
        return input("We can't hear you at the moment, type here instead: ")


def startup_check():
    if not os.path.isfile(LOG_FILE) or not os.access(LOG_FILE, os.R_OK):
        print("Either file is missing or is not readable, creating file...")
        with open(LOG_FILE, 'w') as db_file:
            json.dump({"chats": []}, db_file, ensure_ascii=False, indent=4)


def get_user_input(use_speech):
    if use_speech:
        return transcribe()
    else:
        return input("User: ")


def get_persona(context):
    display = ' | '.join(list(personas.keys()))
    while True:
        choice = input(f"Choose your fighter:\n{display}\n")
        if choice in personas:
            context[0] = {"role": "system", "content": personas[choice]}
            return choice, context


def log_chat_session(context):
    session_log = {"start": start_time, "end": current_time_str(), "content": context}
    with open(LOG_FILE, "r", encoding='utf-8') as jsonFile:
        old_data = json.load(jsonFile)
    old_data["chats"].append(session_log)
    with open(LOG_FILE, "w") as jsonFile:
        json.dump(old_data, jsonFile, ensure_ascii=False, indent=4)


def main():
    startup_check()

    context_arr = [{"role": "system", "content": ""}]
    agent, context_arr = get_persona(context_arr)
    voice_opt = speech_prompt()

    while True:
        try:
            user_input = get_user_input(voice_opt)
        except KeyboardInterrupt:
            log_chat_session(context_arr)
            print("\nAuf Wiedersehen!")
            sys.exit()

        if user_input == "new":
            agent, context_arr = get_persona(context_arr)
            continue
        if user_input == "switch":
            agent, context_arr = get_persona(context_arr)
            continue

        context_arr.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
            model=MODEL_ID,
            messages=context_arr
        )

        assist = response.choices[0].message
        cost = response.usage.total_tokens
        print(f"\n{agent}:\n{assist.content}\nCost: USD {cost * 0.002 / 1000}\n")
        engine.say(assist.content)
        engine.runAndWait()
        context_arr.append(assist)


if __name__ == "__main__":
    start_time = current_time_str()
    main()