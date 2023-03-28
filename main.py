import os
import openai
import time
import datetime
import sys
import json
import pyttsx3

engine = pyttsx3.init()

personas = json.load(open('personas.json', 'r'))
openai.api_key = os.getenv("OPENAI_API_KEY")

display = ' <=> '.join(list(personas.keys()))
while True:
    choice = input(f"Choose your fighter:\n{display}\n")
    if choice in personas:
        context_acc = [{"role": "system", "content": personas[choice]}]
        break
    else:
        print("Your choice is not available")

with open('log.txt', 'a') as f:
    f.write(f"\n\nSession at {str(datetime.datetime.utcfromtimestamp(time.time()))}")

while True:

    try:
        promptio = input("Prompt:\n")
    except KeyboardInterrupt:
        print("\nAuf Wiedersehen!")
        sys.exit()

    context_acc.append({"role": "user", "content": promptio})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context_acc
    )

    assist=response.choices[0].message
    cost=response.usage.total_tokens
    print(f"\n{assist.role}:\n{assist.content}\nCost: USD {cost*0.002/1000}\n")
    engine.say(assist.content)
    engine.runAndWait()
    context_acc.append(assist)

    with open('log.txt', 'a') as f:
        f.write("\n\n")
        f.write(str(datetime.datetime.utcfromtimestamp(time.time())))
        f.write("\n\n")
        f.write(promptio)
        f.write("\n\n")
        f.write(assist.content)
        f.write("\n\n")