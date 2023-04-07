import io
import os
import openai
import time
import datetime
import sys
import json
import pyttsx3
import speech_recognition as sr


start_tone = "start.mp3"
end_tone = "end.mp3"
def tone(case):
    match case:
        case "start":
            os.system("afplay " + start_tone)
        case "end":
            os.system("afplay " + start_tone)

def time_str():
    return str(datetime.datetime.utcfromtimestamp(time.time()))
start_time = time_str()

# Resource gathering
log_file = "log.json"
model_log = "models.json"
personas = json.load(open('personas.json', 'r'))

# Text to speech settings
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate)

# Voice recognition init
r = sr.Recognizer()
def speech_prompt():
    try:
        choice = input(f"Would you like to talk? (y/n): \n")
        if choice == "y":
            return True
        else:
            return False
    except KeyboardInterrupt:
        print("\nAuf Wiedersehen!")
        sys.exit()

def transcribe():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        print("thinking")
        return r.recognize_whisper_api(audio, api_key=openai.api_key)
    except sr.RequestError as e:
        print("Could not request results from Whisper API")
        return e

# OpenAI init
openai.api_key = os.getenv("OPENAI_API_KEY")
model_ls=openai.Model.list()
model_names = [d["id"] for d in model_ls if "id" in d]
avail_models = filter(lambda string: ("gpt" in string), model_names)
print(str(avail_models))


def startupCheck():
    if os.path.isfile(log_file) and os.access(log_file, os.R_OK):
        # checks if file exists
        print ("File exists and is readable")
    else:
        print ("Either file is missing or is not readable, creating file...")
        with io.open(os.path.join(".", log_file), 'w') as db_file:
            db_file.write(json.dumps({"chats": []}))

def prompting(if_speech, context):
    if if_speech:
        try:
            scribble = transcribe()
            print("\033[3m{}\033[0m".format(scribble), "\n")
            return scribble
        except KeyboardInterrupt:
            session_log = {"start": start_time, "end": time_str(), "content": context}
            json_log(log_file, "chats", session_log, "log")
            print("\nAuf Wiedersehen!")
            sys.exit()
        except sr.RequestError:
            return input("We can't hear you at the moment, type here instead:\n")
    else:
        return input("User (type \"new\" for session change):\n")


def json_log(f_name, key, data, mode):
    match mode:
        case "log":
            with open(f_name, "r", encoding='utf-8') as jsonFile:
                old_data = json.load(jsonFile)
            old_data[key].append(data)
            with open(f_name, "w") as jsonFile:
                json.dump(old_data, jsonFile, ensure_ascii=False, indent=4)
        case "overwrite":
            with open(f_name, mode, encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

def persona_input(if_init, context):
    display = ' | '.join(list(personas.keys()))
    while True:
        try:
            choice = input(f"Choose your fighter:\n{display}\n")
        except KeyboardInterrupt:
            session_log = {"start": start_time, "end": time_str(), "content": context}
            json_log(log_file, "chats", session_log, "log")
            print("\nAuf Wiedersehen!")
            sys.exit()
        if choice in personas:
            if if_init:
                try:
                    context = [{"role": "system", "content": personas[choice]}]
                except UnboundLocalError:
                    print(str(context))
                    sys.exit()
            else:
                session_log = {"start": start_time, "end": time_str(), "content": context}
                json_log(log_file, "chats", session_log, "log")
                context = [{"role": "system", "content": personas[choice]}]
            return choice, context
            break
        else:
            print("Your choice is not available")

# # # #

def main():
    startupCheck()

    context_arr = []

    agent, context_arr = persona_input(True, context_arr)
    voice_opt = speech_prompt()
    while True:
        try:
            promptio = prompting(voice_opt, context_arr)
        except KeyboardInterrupt:
            session_log = {"start": start_time, "end": time_str(), "content": context_arr}
            json_log(log_file, "chats", session_log, "log")
            print("\nAuf Wiedersehen!")
            sys.exit()
        if promptio == "new":
            agent, context_arr = persona_input(False, context_arr)
            continue

        context_arr.append({"role": "user", "content": promptio})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=context_arr
        )

        assist=response.choices[0].message
        cost=response.usage.total_tokens
        print(f"\n{agent}:\n{assist.content}\nCost: USD {cost*0.002/1000}\n")
        engine.say(assist.content)
        engine.runAndWait()
        context_arr.append(assist)

main()