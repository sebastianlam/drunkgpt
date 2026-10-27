# DrunkGPT CLI Chatbot

A terminal chatbot with streaming replies, persona selection, optional readback, and an optional local model.

## Features

- **Persona loading** from `personas.json`.
- **Streaming chat** on the OpenAI Python SDK v1.
- **Local models** through [Ollama](https://ollama.com). Pick a discovered `ollama:<name>` entry, or type one at the model prompt.
- **Readback** of finished sentences through `pyttsx3` when that engine can start. Text chat still runs when it cannot.
- **Dictation** through Whisper when `OPENAI_API_KEY` is set and a microphone is available.
- **Session logging** to `log.json`.
- **Unit tests** for personas, logging, speech, and the chat loop.

## Installation

Requires Python 3.11+ and [Poetry](https://python-poetry.org/). PortAudio is needed only for microphone input.

```sh
git clone https://github.com/sebastianlam/drunkgpt.git
cd drunkgpt
poetry install
export OPENAI_API_KEY=<your_key>
poetry run python main.py
```

Without `OPENAI_API_KEY`, the menu is limited to models Ollama is serving on localhost. You can also type a model id when nothing is discovered.

`setup.sh` installs Poetry's Python dependencies and PortAudio on Linux and macOS. It reads `OPENAI_API_KEY` if you paste one, and it does not print the key.

## Commands

Inside a chat:

- `new` saves the current session and picks another persona.
- `quit` saves and exits.
- A blank line is ignored.
- A single space drops queued readback.

## Development

```sh
pytest -q
```

## Project layout

```
main.py            CLI entry point
chat.py            chat loop, model choice, streaming
persona.py         persona loading
speech.py          readback worker
logging_utils.py   session log
personas.json      persona definitions
tests/             unit tests
experiments/       standalone Ollama streaming sketch
```

## Next steps

- Microphone input still needs a working PortAudio device. The Whisper upload itself is covered without one.
- Readback is still the operating-system voice.
