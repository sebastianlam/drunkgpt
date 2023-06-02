import os, openai, sys, time, pyttsx3

openai.api_key = os.getenv("OPENAI_API_KEY")

engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", rate * 0.9)

def sink():
    total, pieces = [], []
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "Why is the sky blue? Philosophise about Rayleigh scattering"
        }],
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            total.append(content)
            pieces.append(content)
            print(content, end="", flush=True)
            # print(chunk, end="", flush=True)
            if content in [
                "."      , ".\n", ".\n\n",
                ",", ", ", ",\n", ",\n\n",
                "!", "! ", "!\n", "!\n\n",
                "?", "? ", "?\n", "?\n\n",
                ":", ": ", ":\n", ":\n\n",
                ";", "; ", ";\n", ";\n\n",
                "\n", "\n\n", "\n\n\n",
            ]:
                print("<<<", end="", flush=True)
                line = "".join(pieces)
                # print(f"\n||||{line}||||\n")
                pieces = []
            
    final = "".join(total)
    print(final)
def main():
    sink()

if __name__ == "__main__":
    main()