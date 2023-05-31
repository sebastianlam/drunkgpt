import os, openai, sys, time, pyttsx3

openai.api_key = os.getenv("OPENAI_API_KEY")

write = sys.stdout.write

engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", rate * 0.9)

def talk(string):
    engine.say(string)
    engine.runAndWait()

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
                talk(line)
                pieces = [] 
            
    final = ''.join(total)
    print(final)
def main():
    sink()

main()