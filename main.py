import asyncio
import json
import os
import queue
import sys
import threading

from chat import (
    ChatSession,
    ask_rate,
    chat_loop,
    choose_model,
    choose_persona,
    drain_queue,
    list_ollama_model_ids,
    make_complete,
    menu_from_ids,
    transcription_text,
)
from logging_utils import session_log, time_str
from persona import load_personas, persona_display as build_persona_display
from speech import tts_worker


LOG_FILE = "log.json"
PERSONAS_FILE = "personas.json"


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        print("\nAuf Wiedersehen!")
        sys.exit(0)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def startup_check(log_file: str) -> None:
    if os.path.isfile(log_file) and os.access(log_file, os.R_OK):
        print("Log loaded.")
        return
    print("Either file is missing or is not readable, creating file...")
    with open(log_file, "w", encoding="utf-8") as handle:
        json.dump({"chats": []}, handle)


def discover_models():
    """List OpenAI chat models when a key is set, plus any local Ollama models."""
    ids = []
    client = None
    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import APIConnectionError, APIError, AuthenticationError, OpenAI

            client = OpenAI()
            ids.extend(model.id for model in client.models.list())
        except AuthenticationError as exc:
            print(f"Invalid key or failed auth: {exc}")
            client = None
        except (APIError, APIConnectionError) as exc:
            print(f"Services unavailable, try again later: {exc}")
            client = None
    else:
        print("OPENAI_API_KEY is not set. OpenAI models will be skipped.")
    ids.extend(list_ollama_model_ids())
    return client, menu_from_ids(ids)


def transcribe_microphone(openai_client):
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 5
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=recognizer.operation_timeout)
    print("thinking")
    return transcription_text(openai_client, audio)


def start_speech(rate: int):
    speech_queue: queue.Queue = queue.Queue()

    def runner():
        asyncio.run(tts_worker(speech_queue, rate))

    thread = threading.Thread(target=runner, name="tts", daemon=True)
    thread.start()
    return speech_queue, thread


def main() -> None:
    sys.excepthook = handle_exception
    print("Welcome to the chatbot!")
    try:
        startup_check(LOG_FILE)
        speech_rate = ask_rate(input)
        openai_client, models = discover_models()
        model = choose_model(input, models)
        personas = load_personas(PERSONAS_FILE)
        options = build_persona_display(personas)
        agent, context = choose_persona(
            input,
            options,
            personas,
            False,
            [],
            time_str(),
            model,
            LOG_FILE,
            session_log,
        )
        voice = input("Enable dictated input? (y/n): ").strip().lower() == "y"
    except (KeyboardInterrupt, EOFError):
        print("\nAuf Wiedersehen!")
        return

    if voice and openai_client is None:
        print("Dictation needs OPENAI_API_KEY. Continuing with typed input.")
        voice = False

    speech_queue, thread = start_speech(speech_rate)
    session = ChatSession(
        context=context,
        model=model,
        agent=agent,
        personas=personas,
        persona_options=options,
        voice=voice,
        log_file=LOG_FILE,
        start_time=time_str(),
        input_fn=input,
        complete=make_complete(openai_client),
        enqueue=speech_queue.put,
        clear_speech=lambda: drain_queue(speech_queue),
        wait_for_speech=speech_queue.join,
        log_fn=session_log,
        time_fn=time_str,
        transcribe_fn=(lambda: transcribe_microphone(openai_client)) if openai_client else None,
    )
    try:
        chat_loop(session)
    finally:
        drain_queue(speech_queue)
        speech_queue.put(None)
        thread.join(timeout=10)


if __name__ == "__main__":
    main()
