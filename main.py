import io
import os
import openai
import datetime
import sys
import json
import pyttsx3
import speech_recognition as sr
from playsound import playsound
import sys


playsound("audio/sniper.mp3")
print("Initialising...")


def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
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
personas = json.load(open(PERSONAS_FILE, "r"))
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

# avail_details = [d for d in model_ls["data"] if d["id"] in model_str]
# print(avail_details)

# Text to speech settings
engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", rate)


# Voice recognition init
r = sr.Recognizer()
r.operation_timeout = 5


def time_str():
    return str(datetime.datetime.utcnow())


def startupCheck():
    if os.path.isfile(LOG_FILE) and os.access(LOG_FILE, os.R_OK):
        # checks if file exists
        print("Log loaded.")
    else:
        print("Either file is missing or is not readable, creating file...")
        with io.open(os.path.join(".", LOG_FILE), "w") as db_file:
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
            continue
        except KeyboardInterrupt:
            session_log(context, time, model, True)
        if choice in options:
            if is_continue:
                session_log(context, time, model, False)
            context = [{"role": "system", "content": personas[options[choice]]}]
            print(f"You have chosen {options[choice]}")
            return options[choice], context
        else:
            print("Your choice is not available")


def prompting(is_speech, context):
    if is_speech:
        try:
            preview = transcribe()
            talk("hmm...")
            print("\033[3m{}\033[0m".format(preview), "\n")
            return preview
        except sr.RequestError:
            return input("We can't hear you at the moment, type here instead:\n")
    else:
        return input("User:\n")


####################################################################################################


def main():

    start_time = time_str()
    startupCheck()
    context_arr = []
    voice_opt = speech_prompt()
    MODEL_ID = model_prompt(model_display)
    agent, context_arr = persona_input(
        persona_display, False, context_arr, start_time, MODEL_ID
    )
    print('(input "new" for session change)')

    while True:
        try:
            promptio = prompting(voice_opt, context_arr)
        except KeyboardInterrupt:
            session_log(context_arr, start_time, MODEL_ID, True)
        if promptio.lower() == "new":
            agent, context_arr = persona_input(
                persona_display, True, context_arr, start_time, MODEL_ID
            )
            start_time = time_str()
            continue
        if promptio.lower() == "":
            print("Give me something mate.")
            continue
        context_arr.append({"role": "user", "content": promptio})
        response = openai.ChatCompletion.create(model=MODEL_ID, messages=context_arr)

        # print(response)

        assist = response.choices[0].message
        cost = response.usage
        cost_display = "  ".join(
            [*["(" + str(k) + ") " + str(v) for k, v in cost.items()]]
        )
        print(f"\n{agent}:\n{assist.content}\n{cost_display}\n")
        context_arr.append(assist)
        try:
            talk(assist.content)
        except KeyboardInterrupt:
            session_log(context_arr, start_time, MODEL_ID, True)


main()
