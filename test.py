import os, openai, sys, time

openai.api_key = os.getenv("OPENAI_API_KEY")

write = sys.stdout.write


def sink():
    total = []
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "write a 20 word poem"
        }],
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            total.append(content)
            print(content, end="", flush=True)
    final = ''.join(total)

def main():
    sink()

main()