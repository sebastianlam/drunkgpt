import io, os, openai, datetime, sys, json, threading, time
import speech_recognition as sr
from playsound import playsound


# Thread config
running = True


# Utils
def time_str():
    return str(datetime.datetime.utcnow())
def startupCheck():
    if os.path.isfile(LOG_FILE) and os.access(LOG_FILE, os.R_OK):
        # checks if file exists
        print("Log loaded.")
    else:
        print("Either file is missing or is not readable, creating file...")
        with io.open(os.path.join(".", LOG_FILE), "w") as db_file:
            db_file.write(json.dumps({"chats": []}))
def json_log(f_name, key, data):
    with open(f_name, "r", encoding="utf-8") as jsonFile:
        old_data = json.load(jsonFile)
    old_data[key].append(data)
    with open(f_name, "w") as jsonFile:
        json.dump(old_data, jsonFile, ensure_ascii=False, indent=4)
def session_log(context, init_time, model):
    log_content = {
        "start": init_time,
        "end": time_str(),
        "model": model,
        "content": context,
    }
    json_log(LOG_FILE, "chats", log_content)


# Constants and configurations
LOG_FILE = "log.json"
PERSONAS_FILE = "personas.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Load personas
personas = json.load(open(PERSONAS_FILE, "r"))
persona_options = list(personas.keys())
persona_display = dict(enumerate(persona_options, 1))


# OpenAI init
openai.api_key = OPENAI_API_KEY
try:
    model_ls = openai.Model.list()
except (openai.AuthenticationError, openai.PermissionError) as e:
    print(f"Invalid key or failed auth: {e}")
    sys.exit()
except (openai.InvalidRequestError, openai.APIError, openai.ServiceUnavailableError, openai.APIConnectionError) as e:
    print(f"Services unavailable, try again later: {e}")
    sys.exit()
model_names = [d["id"] for d in model_ls["data"] if "id" in d]
gpt_options = filter(lambda string: "gpt" in string, model_names)
model_str = list(gpt_options)
model_display = dict(enumerate(model_str, 1))


# Voice recognition init
r = sr.Recognizer()
r.operation_timeout = 5


# Speech init and functions
speech_queue = []
is_block = False
def text_to_speech():
    global running, speech_queue, is_block
    while running:
        if len(speech_queue) > 0:
            is_block = True
            try:
                sentence = speech_queue[0]
                for ch in ["\n", "`", "\"", "$("]:
                    if ch in sentence:
                        sentence = sentence.replace(ch, ', ')
                if sentence != "":
                    os.system(f'say \"{sentence}\"')
                speech_queue.pop(0)
            except KeyboardInterrupt:
                print("clearing speech queue... ", end="",flush=True)
                speech_queue = []
                print("Done.", flush=True)
        else:
            is_block = False
            time.sleep(0.1)


def transcribe():
    with sr.Microphone() as source:
        playsound("audio/start.mp3")
        print("Listening...")
        audio = r.listen(source, timeout=r.operation_timeout)
    try:
        playsound("audio/end.mp3")
        print("thinking")
        return r.recognize_whisper_api(audio, api_key=openai.api_key)
    except sr.RequestError as e:
        print("Could not request results from Whisper API")
        return e
    except sr.WaitTimeoutError as e:
        print("Timeout error: " + str(e))
        return e


def speech_prompt():
    try:
        choice = input("Enable dictated input? (y/n): ")
        return choice.lower() == "y"
    except KeyboardInterrupt:
        print("\nAuf Wiedersehen!")
        sys.exit()


def model_prompt(models):
    display = "\n".join([*["(" + str(k) + ") " + str(v) for k, v in models.items()]])
    while True:
        try:
            choice = int(input(f"Choose your model:\n{display}\n"))
        except ValueError:
            print("Type the corresponding number please.")
            continue
        except KeyboardInterrupt:
            return e
        if choice in models:
            print(f"You have chosen {models[choice]}")
            return models[choice]
        else:
            print("Your choice is not available")


def persona_input(options, is_continue, context, init_time, model):
    """

    """
    display = "\n".join([*["(" + str(k) + ") " + str(v) for k, v in options.items()]])
    while True:
        try:
            choice = int(input(f"Choose your fighter:\n{display}\n"))
        except ValueError:
            print("Type the corresponding number please.")
            continue
        except KeyboardInterrupt as e:
            return e
        if choice in options:
            if is_continue:
                session_log(context, init_time, model)
            context = [{"role": "system", "content": personas[options[choice]]}]
            print(f"You have chosen {options[choice]}")
            return options[choice], context
        else:
            print("Your choice is not available")


def prompting(is_speech):
    if is_speech:
        try:
            preview = transcribe()
            # talk("hmm...")
            os.system(f'say "hmm..."')
            print("\033[3m{}\033[0m".format(preview), "\n")
            return preview
        except sr.RequestError:
            return input("We can't hear you at the moment, type here instead:\n")
    else:
        try:
            return input("User:\n")
        except KeyboardInterrupt as e:
            return e

def chat_loop():
    global running, speech_queue, is_block, agent, voice_opt, MODEL_ID, voice_opt, context_arr
    local_total, local_pieces = [], []
    while True:
        try:
            promptio = prompting(voice_opt)
            if promptio.lower() == "new":
                agent, context_arr = persona_input(
                    persona_display, True, context_arr, start_time, MODEL_ID
                )
                start_time = time_str()
                continue
            if promptio.lower() == "":
                print("Give me something mate.")
                continue
            context_arr.append({"role": "user", "content": promptio})
            is_block = True
            try:
                for chunk in openai.ChatCompletion.create(
                    model=MODEL_ID, messages=context_arr, stream=True
                ):
                    content = chunk["choices"][0].get("delta", {}).get("content")
                    if content is not None:
                        # local_total.append(content)
                        local_pieces.append(content)
                        local_total.append(content)
                        print(content, end="", flush=True)
                        # print(chunk, end="", flush=True)
                        if content in [".", ".\n", ".\n\n", ", ", ",\n", ",\n\n", "!", "! ", "!\n", "!\n\n", "?", "? ", "?\n", "?\n\n", ":", ": ", ":\n", ":\n\n", ";", "; ", ";\n", ";\n\n", "\n", "\n\n", "\n\n\n",]:
                            sentence = "".join(local_pieces)
                            speech_queue.append(sentence)
                            local_pieces = []
                    else:
                        sentence = "".join(local_pieces)
                        speech_queue.append(sentence)
                        local_pieces = []
            except (openai.InvalidRequestError, openai.APIError, openai.ServiceUnavailableError, openai.APIConnectionError) as e:
                print(f"Openai services shutdown during query, check-in later: {e}")
                return KeyboardInterrupt

            assist = "".join(local_total)
            local_total = []
            context_arr.append({"role": "assistant", "content": assist})
            # cost = response.usage
            # cost_display = "  ".join(
            #     [*["(" + str(k) + ") " + str(v) for k, v in cost.items()]]
            # )
            # print(f"\n{agent}:\n{assist.content}\n{cost_display}\n")
            
        except KeyboardInterrupt:
            assist = "".join(local_total)
            context_arr.append({"role": "assistant", "content": assist})
            session_log(context_arr, start_time, MODEL_ID)
            print("\nAuf Wiedersehen!")
            sys.exit()
        try:
            wait_counter = 0
            print("DEBUG: LOOP ATTEMPT")
            while len(speech_queue) > 0 and is_block == True:
                wait_counter += 1
                print(f"{wait_counter}, ", end="", flush=True)
                time.sleep(1)
            print("DEBUG: NEW LOOP")
            continue
        except KeyboardInterrupt:
            print("\nSpeech skipped.\n")
            continue



try:
    startupCheck()
    context_arr = []
    start_time = time_str()
    voice_opt = speech_prompt()
    MODEL_ID = model_prompt(model_display)
    agent, context_arr = persona_input(
        persona_display, False, context_arr, start_time, MODEL_ID
    )
except KeyboardInterrupt as e:
    print(e)
    sys.exit()

def main():

    print("(Type \"new\" for session change)\n")

    chat_thread = threading.Thread(target=chat_loop)
    chat_thread.start()

    speech_thread = threading.Thread(target=text_to_speech)
    speech_thread.start()

    chat_thread.join()
    speech_thread.join()


if __name__ == "__main__":
    main()