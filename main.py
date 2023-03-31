import os
import openai
import time
import datetime
import sys
import json
import pyttsx3

def time_str():
    return str(datetime.datetime.utcfromtimestamp(time.time()))

start_time = time_str()

log_file = "log.json"
model_log = "models.json"
personas = json.load(open('personas.json', 'r'))
openai.api_key = os.getenv("OPENAI_API_KEY")


engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-30)

model_ls=openai.Model.list()
model_names = [d["id"] for d in model_ls if "id" in d]

avail_models = filter(lambda string: ("gpt" in string), model_names)
print(avail_models)

context_arr = []

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

def persona_input(if_keep):
    display = ' | '.join(list(personas.keys()))
    while True:
        try:
            choice = input(f"Choose your fighter:\n{display}\n")
        except KeyboardInterrupt:
            session_log = {"start": start_time, "end": time_str(), "content": context_arr}
            json_log(log_file, "chats", session_log, "log")
            print("\nAuf Wiedersehen!")
            sys.exit()
        if choice in personas:
            if if_keep:
                context_arr[0] = {"role": "system", "content": personas[choice]}
                return choice
                break
            context_arr.append({"role": "system", "content": personas[choice]})
            return choice
            break
        else:
            print("Your choice is not available")

def main():
    agent = persona_input(False)
    while True:
        try:
            promptio = input("User:\n")
        except KeyboardInterrupt:
            session_log = {"start": start_time, "end": time_str(), "content": context_arr}
            json_log(log_file, "chats", session_log, "log")
            print("\nAuf Wiedersehen!")
            sys.exit()
        
        if promptio == "new":
            agent = persona_input(False)
            continue
        if promptio == "switch":
            agent = persona_input(True)
            continue

        context_arr.append({"role": "user", "content": promptio})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=context_arr
        )

        assist=response.choices[0].message
        cost=response.usage.total_tokens
        print(f"\n{assist.role}:\n{assist.content}\nCost: USD {cost*0.002/1000}\n")
        engine.say(assist.content)
        engine.runAndWait()
        context_arr.append(assist)

        with open('log.txt', 'a') as f:
            f.write("\n\n")
            f.write(time_str())
            f.write("\n\n")
            f.write(promptio)
            f.write("\n\n")
            f.write(assist.content)
            f.write("\n\n")

main()