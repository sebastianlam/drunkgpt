import os
import openai
import time
import datetime
import sys
import json
import pyttsx3

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
            with open(f_name, "r") as jsonFile:
                old_data = json.load(jsonFile)
            old_data[key] = data
            with open(f_name, "w") as jsonFile:
                json.dump(old_data, jsonFile)
        case "overwrite":
            with open(f_name, mode, encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

def time_str():
    return str(datetime.datetime.utcfromtimestamp(time.time()))

def persona_input(if_keep):
    display = ' | '.join(list(personas.keys()))
    while True:
        try:
            choice = input(f"Choose your fighter:\n{display}\n")
        except KeyboardInterrupt:
            print("\nAuf Wiedersehen!")
            sys.exit()
        if choice in personas:
            if if_keep:
                context_arr[0] = {"role": "system", "content": personas[choice]}
                break
            context_arr.append({"role": "system", "content": personas[choice]})
            break
        else:
            print("Your choice is not available")

with open('log.txt', 'a') as f:
    f.write(f"\n\nSession at {time_str()}")

def main():
    while True:

        try:
            promptio = input("Prompt:\n")
        except KeyboardInterrupt:
            print("\nAuf Wiedersehen!")
            sys.exit()

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