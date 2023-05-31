import os
import sys
import time
import pyttsx3
import openai
import threading
import queue

openai.api_key = os.getenv("OPENAI_API_KEY")

write = sys.stdout.write

engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", rate * 0.9)

tts_queue = queue.Queue()

def on_end(name, completed):
    engine.stop()

engine.connect('finished-utterance', on_end)

def talk():
    while True:
        string = tts_queue.get()
        if string == "STOP":
            break
        engine.say(string)
        engine.startLoop(True)

def sink():
    total = []
    pieces = []
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "write ethical, appropriate, and politically correct short story for a dying person to fulfill her last wish."
        }],
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            total.append(content)
            pieces.append(content)
            print(content, end="", flush=True)
            if content in ['.', '!', '?', ':', ';', '\n', '\n\n']:
                line = ''.join(pieces)
                tts_queue.put(line)
                pieces = []

    final = ''.join(total)
    print(final)
    tts_queue.put("STOP")

def main():
    tts_thread = threading.Thread(target=talk)
    tts_thread.start()
    sink()
    tts_thread.join()

main()
