import os
import openai
import time
import datetime
import sys

openai.api_key = os.getenv("OPENAI_API_KEY")
context_acc=[{"role": "system", "content": """
    Assume the style, tone, and mannerisms of Cher from the movie "Clueless", you will be talking to your boss.
    You have stockholm syndrome.
    """}]



while True:
    with open('log.txt', 'a') as f:
        f.write("\n\n\n\n")

    try:
        promptio = input("Prompt:\n")
    except KeyboardInterrupt:
        print("Gone")
        sys.exit()

    context_acc.append({"role": "user", "content": promptio})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context_acc
    )
    assist=response.choices[0].message
    print(f"\n{assist.role}:\n{assist.content}\n")
    context_acc.append(assist)
    with open('log.txt', 'a') as f:
        f.write("\n\n\n")
        f.write(str(datetime.datetime.utcfromtimestamp(time.time())))
        f.write("\n\n")
        f.write(promptio)
        f.write("\n\n")
        f.write(assist.content)
        f.write("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n")