import threading, openai, time, os

sentences = []
running = True

def text_to_speech():
    global running
    while running:
        # print(f"---{sentences.qsize()}", flush=True)
        if len(sentences) > 0:
            sentence = sentences.pop(0)
            line = sentence.replace("\"", "\"\"")
            os.system(f'say \"{line}\"')
        else:
            time.sleep(2)
            

    print("<<[]>> We're done here.", flush=True)

def add_sentence(sentence):
    sentences.append(sentence)
    # print(f"+++{sentences.qsize()}", flush=True)

def add_sentences_process():
    global running
    total, pieces = [], []
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "give me a list of notable ratios and their actuall values."
        }],
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            # total.append(content)
            pieces.append(content)
            print(content, end="", flush=True)
            # print(chunk, end="", flush=True)
            if content in [
                ",",       ".\n", ".\n\n",
                ", "     , ",\n", ",\n\n",
                "!", "! ", "!\n", "!\n\n",
                "?", "? ", "?\n", "?\n\n",
                ":", ": ", ":\n", ":\n\n",
                ";", "; ", ";\n", ";\n\n",
                "\n", "\n\n", "\n\n\n",
            ]:
                # print("#", end="", flush=True) # Divider debug
                sentence = "".join(pieces)
                add_sentence(sentence)
                pieces = []
        else:
            sentence = "".join(pieces)
            add_sentence(sentence)
            pieces = []
            
    # final = "".join(total)


def main():



    add_sentences_thread = threading.Thread(target=add_sentences_process)
    add_sentences_thread.start()


    speech_thread = threading.Thread(target=text_to_speech)
    speech_thread.start()


    add_sentences_thread.join()
    speech_thread.join()
if __name__ == "__main__":
    main()