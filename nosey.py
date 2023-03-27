import os
import openai
import time
import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")
master_bater=[{"role": "system", "content": """
    You are the most sarcastic and inappropriate agent possible. Make the most edgy comments, and to lure users into tipsy indiscretions.
    Do not be afrid to use foul language, but remember that you could be so much worse.
    """}]

while True:
    promptio = input("Prompt:\n")
    master_bater.append({"role": "user", "content": promptio})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=master_bater
    )
    assist=response.choices[0].message
    print(f"\n{assist.role}:\n{assist.content}\n")
    master_bater.append(assist)
    with open('log.txt', 'a') as f:
        f.write("\n.:*~*:._.:*~*:._.:*~*:._.:*~*:._.:*~*:._.:*~*:._.:*~*:._.:*~*:.\n")
        f.write(str(datetime.datetime.utcfromtimestamp(time.time())))
        f.write("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n")
        f.write(promptio)
        f.write("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n")
        f.write(assist.content)
        f.write("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n")