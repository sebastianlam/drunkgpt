# I have made several improvements to the code in terms of performance, modularity, and security. The changes include refactoring the code into separate functions, handling exceptions more effectively, and using context managers for file handling. Here's the updated code:

# ```python
import io
import os
import openai
import datetime
import sys
import json
import pyttsx3
import speech_recognition as sr
from playsound import playsound

playsound("audio/sniper.mp3")
print("Initialising...")


def get_base_prefix_compat():
    return (
        getattr(sys, "base_prefix", None)
        or getattr(sys, "real_prefix", None)
        or sys.prefix
    )


def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix


print(get_base_prefix_compat())
print(in_virtualenv())

# Constants and configurations
LOG_FILE = "log.json"
PERSONAS_FILE = "personas.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load personas
with open(PERSONAS_FILE, "r") as f:
    personas = json.load(f)

persona_options = list(personas.keys())
persona_display = dict(enumerate(persona_options, 1))

# OpenAI init
openai.api_key = OPENAI_API_KEY
model_ls = openai.Model.list()

# Load available models
model_names = [d["id"] for d in model_ls["data"] if "id" in d]
gpt_options = filter(lambda string: "gpt" in string, model_names)
model_str = list(gpt_options)
model_display = dict(enumerate(model_str, 1))

# Text to speech settings
engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", rate)

# Voice recognition init
r = sr.Recognizer()
r.operation_timeout = 5


def time_str():
    return str(datetime.datetime.utcnow())


def startup_check(log_file):
    if os.path.isfile(log_file) and os.access(log_file, os.R_OK):
        print("Log loaded.")
    else:
        print("Either file is missing or is not readable, creating file...")
        with io.open(os.path.join(".", log_file), "w") as db_file:
            db_file.write(json.dumps({"chats": []}))


def json_log(f_name, key, data):
    with open(f_name, "r", encoding="utf-8") as jsonFile:
        old_data = json.load(jsonFile)
    old_data[key].append(data)
    with open(f_name, "w") as jsonFile:
        json.dump(old_data, jsonFile, ensure_ascii=False, indent=4)


def session_log(context, init_time, model, is_end):
    log_content = {
        "start": init_time,
        "end": time_str(),
        "model": model,
        "content": context,
    }
    json_log(LOG_FILE, "chats", log_content)
    if is_end:
        print("\nAuf Wiedersehen!")
        sys.exit()


def talk(string):
    engine.say(string)
    engine.runAndWait()


def transcribe():
    with sr.Microphone() as source:
        playsound("audio/start.mp3")
        print("Listening...")
        audio = r.listen(source, timeout=r.operation_timeout)
    try:
        playsound("audio/end.mp3")
        print("thinking")
        return r.recognize_whisper_api(audio, api_key=openai.api_key)
    except sr.RequestError as e:
        print("Could not request results from Whisper API")
        return e
    except sr.WaitTimeoutError as e:
        print("Timeout error: " + str(e))
        return e


def speech_prompt():
    try:
        choice = input("Would you like to talk? (y/n): ")
        return choice.lower() == "y"
    except KeyboardInterrupt:
        print("\nAuf Wiedersehen!")
        sys.exit()


def model_prompt(models):
    display = "\n".join([*["(" + str(k) + ") " + str(v) for k, v in models.items()]])
    while True:
        try:
            choice = int(input(f"Choose your model:\n{display}\n"))
        except ValueError:
            print("Type the corresponding number please.")
            continue
        except KeyboardInterrupt:
            print("\nAuf Wiedersehen!")
            sys.exit()
        if choice in models:
            print(f"You have chosen {models[choice]}")
            return models[choice]
        else:
            print("Your choice is not available")


def persona_input(options, is_continue, context, time, model):
    display = "\n".join([*["(" + str(k) + ") " + str(v) for k, v in options.items()]])
    while True:
        try:
            choice = int(input(f"Choose your fighter:\n{display}\n"))
        except ValueError:
            print("Type the corresponding number please.")