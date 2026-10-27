"""Chat-loop helpers for the DrunkGPT CLI.

The functions here are deliberately free of network and audio side effects so
the streaming, persona, and model-selection behaviour can be tested directly.
"""

from __future__ import annotations

import io
import queue
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator


SENTENCE_BOUNDARIES = frozenset(
    {
        ".",
        ".\n",
        ".\n\n",
        ", ",
        ",\n",
        ",\n\n",
        "!",
        "! ",
        "!\n",
        "!\n\n",
        "?",
        "? ",
        "?\n",
        "?\n\n",
        ":",
        ": ",
        ":\n",
        ":\n\n",
        ";",
        "; ",
        ";\n",
        ";\n\n",
        "\n",
        "\n\n",
        "\n\n\n",
    }
)

# Matched by class name so tests can raise stand-ins without importing SDKs.
PROVIDER_ERROR_NAMES = frozenset(
    {
        "APIError",
        "APIConnectionError",
        "APITimeoutError",
        "APIStatusError",
        "RateLimitError",
        "AuthenticationError",
        "ConnectError",
        "ConnectionError",
        "ResponseError",
    }
)

# Substrings that mark models the chat completions call cannot use.
_NON_CHAT_MARKERS = (
    "whisper",
    "tts",
    "dall-e",
    "embedding",
    "moderation",
    "babbage",
    "davinci",
    "realtime",
    "transcribe",
    "sora",
    "audio",
    "image",
)


def is_provider_error(exc: BaseException) -> bool:
    return exc.__class__.__name__ in PROVIDER_ERROR_NAMES


def is_selectable_model(model_id: str) -> bool:
    """Return True for chat models and for explicit Ollama ids."""
    if model_id.startswith("ollama:"):
        return bool(model_id.split(":", 1)[1].strip())
    lowered = model_id.lower()
    return not any(marker in lowered for marker in _NON_CHAT_MARKERS)


def menu_from_ids(model_ids: Iterable[str]) -> dict[int, str]:
    selectable: list[str] = []
    seen: set[str] = set()
    for model_id in model_ids:
        if model_id in seen or not is_selectable_model(model_id):
            continue
        seen.add(model_id)
        selectable.append(model_id)
    return dict(enumerate(selectable, 1))


def resolve_model_choice(raw: str, models: dict[int, str]) -> str | None:
    """Map a menu entry or an ``ollama:<name>`` id to a model id."""
    text = raw.strip()
    if text.lower().startswith("ollama:"):
        name = text.split(":", 1)[1].strip()
        if not name:
            return None
        return f"ollama:{name}"
    if text.isdigit():
        return models.get(int(text))
    return None


def classify_command(prompt: str) -> str:
    if prompt.lower() == "new":
        return "new"
    if prompt.lower() == "quit":
        return "quit"
    if prompt == "":
        return "empty"
    if prompt == " ":
        return "skip"
    return "message"


def ask_rate(read_line: Callable[[str], str]) -> int:
    prompt = "Desired readback words per minute (default = 200): "
    while True:
        raw = read_line(prompt).strip()
        if raw == "":
            return 200
        try:
            rate = int(raw)
        except ValueError:
            print("Type a whole number, or press enter for 200.")
            continue
        if rate <= 0:
            print("Type a whole number, or press enter for 200.")
            continue
        return rate


def choose_model(read_line: Callable[[str], str], models: dict[int, str]) -> str:
    if models:
        display = "\n".join(f"({key}) {value}" for key, value in models.items())
        hint = (
            f"Choose your model:\n{display}\n"
            "Or type ollama:<name> for a local model.\n"
        )
    else:
        hint = "No models discovered. Type a model id, or ollama:<name>:\n"
    while True:
        raw = read_line(hint)
        picked = resolve_model_choice(raw, models)
        if picked is None and not models:
            candidate = raw.strip()
            if candidate and " " not in candidate:
                picked = candidate
        if picked:
            print(f"You have chosen {picked}")
            return picked
        print("Your choice is not available")


def choose_persona(
    read_line: Callable[[str], str],
    options: dict[int, str],
    personas: dict[str, str],
    is_continue: bool,
    context: list,
    init_time: str,
    model: str,
    log_file: str,
    log_fn: Callable,
) -> tuple[str, list]:
    display = "\n".join(f"({key}) {value}" for key, value in options.items())
    while True:
        raw = read_line(f"Choose your fighter:\n{display}\n")
        try:
            choice = int(raw)
        except ValueError:
            print("Type the corresponding number please.")
            continue
        if choice not in options:
            print("Your choice is not available")
            continue
        if is_continue:
            log_fn(log_file, context, init_time, model)
        name = options[choice]
        print(f"You have chosen {name}")
        return name, [{"role": "system", "content": personas[name]}]


def render_stream(
    deltas: Iterable[str | None],
    enqueue: Callable[[str], None],
    write: Callable[[str], None],
) -> str:
    """Print streamed text and enqueue a sentence whenever a chunk ends one.

    A trailing fragment is spoken even when the provider never sends an empty
    closing delta. Empty deltas flush whatever is already buffered.
    """
    pieces: list[str] = []
    total: list[str] = []
    for content in deltas:
        if not content:
            if pieces:
                enqueue("".join(pieces))
                pieces = []
            continue
        pieces.append(content)
        total.append(content)
        write(content)
        if content in SENTENCE_BOUNDARIES:
            enqueue("".join(pieces))
            pieces = []
    if pieces:
        enqueue("".join(pieces))
    return "".join(total)


def openai_deltas(client, model: str, messages: list) -> Iterator[str | None]:
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    for chunk in stream:
        yield chunk.choices[0].delta.content


def text_from_ollama_part(part) -> str | None:
    if isinstance(part, dict):
        message = part.get("message") or {}
        if isinstance(message, dict):
            return message.get("content")
        return getattr(message, "content", None)
    message = getattr(part, "message", None)
    if message is None:
        return None
    return getattr(message, "content", None)


def ollama_deltas(model: str, messages: list, factory: Callable | None = None) -> Iterator[str | None]:
    if factory is None:
        from ollama import Client

        client = Client(timeout=120)
    else:
        client = factory()
    stream = client.chat(model=model, messages=messages, stream=True)
    for part in stream:
        content = text_from_ollama_part(part)
        if content:
            yield content
    yield None


def list_ollama_model_ids(factory: Callable | None = None) -> list[str]:
    """Return ``ollama:<name>`` ids, or an empty list when Ollama is down."""
    try:
        if factory is None:
            from ollama import Client

            client = Client(timeout=2)
        else:
            client = factory()
        listed = client.list()
    except ImportError:
        return []
    except Exception as exc:
        print(f"Ollama is not available ({exc.__class__.__name__}). Local models skipped.")
        return []

    if isinstance(listed, dict):
        models = listed.get("models", [])
    else:
        models = getattr(listed, "models", []) or []

    ids: list[str] = []
    for model in models:
        if isinstance(model, dict):
            name = model.get("model") or model.get("name")
        else:
            name = getattr(model, "model", None) or getattr(model, "name", None)
        if name:
            ids.append(f"ollama:{name}")
    return ids


def make_complete(openai_client, ollama_factory: Callable | None = None) -> Callable:
    def complete(model: str, messages: list) -> Iterator[str | None]:
        if model.startswith("ollama:"):
            name = model.split(":", 1)[1]
            yield from ollama_deltas(name, messages, factory=ollama_factory)
            return
        if openai_client is None:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        yield from openai_deltas(openai_client, model, messages)

    return complete


def transcription_upload(audio) -> tuple:
    """Shape SpeechRecognition audio into the file tuple the Whisper API accepts."""
    return ("speech.wav", io.BytesIO(audio.get_wav_data()), "audio/wav")


def transcription_text(openai_client, audio) -> str:
    result = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=transcription_upload(audio),
    )
    text = getattr(result, "text", None)
    if text is None and isinstance(result, dict):
        text = result.get("text")
    return text or ""


def drain_queue(speech_queue: queue.Queue) -> None:
    while True:
        try:
            speech_queue.get_nowait()
        except queue.Empty:
            return
        else:
            speech_queue.task_done()


def _default_write(text: str) -> None:
    print(text, end="", flush=True)


@dataclass
class ChatSession:
    context: list
    model: str
    agent: str
    personas: dict[str, str]
    persona_options: dict[int, str]
    voice: bool
    log_file: str
    start_time: str
    input_fn: Callable[[str], str]
    complete: Callable
    enqueue: Callable[[str], None]
    clear_speech: Callable[[], None]
    wait_for_speech: Callable[[], None]
    log_fn: Callable
    time_fn: Callable[[], str]
    write: Callable[[str], None] = field(default=_default_write)
    transcribe_fn: Callable[[], str] | None = None


def read_user_text(session: ChatSession) -> str:
    if not session.voice:
        return session.input_fn("User:\n")
    if session.transcribe_fn is None:
        print("Dictation needs OPENAI_API_KEY. Type instead.")
        return session.input_fn("User:\n")
    try:
        preview = session.transcribe_fn()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"We can't hear you at the moment ({exc}). Type here instead.")
        return session.input_fn("User:\n")
    if classify_command(preview) == "message":
        session.enqueue("hmm...")
    print("\033[3m{}\033[0m\n".format(preview))
    return preview


def _log_and_goodbye(session: ChatSession) -> None:
    session.log_fn(session.log_file, session.context, session.start_time, session.model)
    print("\nAuf Wiedersehen!")


def chat_loop(session: ChatSession) -> None:
    print(
        '(Type:\n"new" for session change,\n"quit" to save and quit chat,\n'
        "Space to skip speech queue.)\n"
    )
    while True:
        try:
            prompt = read_user_text(session)
        except (KeyboardInterrupt, EOFError):
            _log_and_goodbye(session)
            return

        command = classify_command(prompt)
        if command == "new":
            try:
                session.agent, session.context = choose_persona(
                    session.input_fn,
                    session.persona_options,
                    session.personas,
                    True,
                    session.context,
                    session.start_time,
                    session.model,
                    session.log_file,
                    session.log_fn,
                )
            except (KeyboardInterrupt, EOFError):
                _log_and_goodbye(session)
                return
            session.start_time = session.time_fn()
            continue
        if command == "empty":
            print("Give me something mate.")
            continue
        if command == "skip":
            session.clear_speech()
            continue
        if command == "quit":
            _log_and_goodbye(session)
            return

        session.context.append({"role": "user", "content": prompt})
        try:
            assist = render_stream(
                session.complete(session.model, session.context),
                session.enqueue,
                session.write,
            )
        except Exception as exc:
            if is_provider_error(exc):
                print(f"client services shutdown during query, check-in later: {exc}")
            else:
                print(f"An error has occurred: {exc}")
            _log_and_goodbye(session)
            return

        session.context.append({"role": "assistant", "content": assist})
        print()
        try:
            session.wait_for_speech()
        except KeyboardInterrupt:
            print("\nSpeech skipped.\n")
            session.clear_speech()
