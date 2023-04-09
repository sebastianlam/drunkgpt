import io
import os
import openai
import datetime
import sys
import json
import pyttsx3
import speech_recognition as sr

def time_str():
    return str(datetime.datetime.utcnow())


# Resource gathering
log_file = "log.json"
model_log = "models.json"
personas = json.load(open('personas.json', 'r'))
persona_options = list(personas.keys())
persona_display = dict(enumerate(persona_options, 1))
print(persona_display)


# OpenAI init
openai.api_key = os.getenv("OPENAI_API_KEY")
model_ls = openai.Model.list()

model_names = [d["id"] for d in model_ls["data"] if "id" in d]
gpt_options = filter(lambda string: "gpt" in string, model_names)
model_str = list(gpt_options)
model_display = dict(enumerate(model_str, 1))
print(model_display)

# avail_details = [d for d in model_ls["data"] if d["id"] in model_str]
# print(avail_details)

def model_prompt(models):
    display = "\n".join([*['(' + str(k) + ') ' + str(v) for k,v in models.items()]])
    while True:
        try:
            choice = int(input(f"Choose your model:\n{display}\n"))
        except KeyboardInterrupt:
            print("\nAuf Wiedersehen!")
            sys.exit()
        if choice in models:
            return models[choice]
        else:
            print("Your choice is not available")


def json_log(f_name, key, data):
    with open(f_name, "r", encoding='utf-8') as jsonFile:
        old_data = json.load(jsonFile)
    old_data[key].append(data)
    with open(f_name, "w") as jsonFile:
        json.dump(old_data, jsonFile, ensure_ascii=False, indent=4)

def session_log(context, init_time, model, if_end):
    log_content = {"start": init_time, "end": time_str(), "model": model, "content": context}
    json_log(log_file, "chats", log_content)
    if if_end:
        print("\nAuf Wiedersehen!")
        sys.exit()

# Text to speech settings
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate)
def talk(string):
    engine.say(string)
    engine.runAndWait()

# Voice recognition init
r = sr.Recognizer()
r.operation_timeout = 5

def transcribe():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, timeout=r.operation_timeout)
    try:
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
            preview = transcribe()
            print("\033[3m{}\033[0m".format(preview), "\n")
            return preview
        except sr.RequestError:
            return input("We can't hear you at the moment, type here instead:\n")
    else:
        return input("User:\n")


def persona_input(options, if_continue, context, time, model):
    display = "\n".join([*['(' + str(k) + ') ' + str(v) for k,v in options.items()]])
    while True:
        try:
            choice = int(input(f"Choose your fighter:\n{display}\n"))
        except KeyboardInterrupt:
            session_log(context, time, model, True)
        if choice in options:
            if if_continue:
                session_log(context, time, model, False)
            context = [{"role": "system", "content": personas[options[choice]]}]
            return options[choice], context
        else:
            print("Your choice is not available")

# # # #

def main():
    start_time = time_str()
    startupCheck()
    context_arr = []
    voice_opt = speech_prompt()
    MODEL_ID = model_prompt(model_display)
    agent, context_arr = persona_input(persona_display, False, context_arr, start_time, MODEL_ID)
    print("(input \"new\" for session change)")

    while True:
        try:
            promptio = prompting(voice_opt, context_arr)
        except KeyboardInterrupt:
            session_log(context_arr, start_time, MODEL_ID, True)
        if promptio.lower() == "new":
            agent, context_arr = persona_input(persona_display, True, context_arr, start_time, MODEL_ID)
            start_time = time_str()
            continue

        context_arr.append({"role": "user", "content": promptio})
        response = openai.ChatCompletion.create(
            model=MODEL_ID,
            messages=context_arr
        )

        assist=response.choices[0].message
        cost=response.usage.total_tokens
        print(f"\n{agent}:\n{assist.content}\nCost: {cost}\n")
        talk(assist.content)
        context_arr.append(assist)

main()