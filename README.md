# DrunkGPT CLI Chatbot

A terminal-based chatbot client supporting streaming responses, persona selection, and optional speech features. This project demonstrates a cross-platform text-to-speech (TTS) queue and a simple test-driven development setup.

## Features
- **Persona loading** – choose predefined styles from `personas.json`.
- **Streaming chat** – responses stream token by token.
- **Asynchronous TTS** – `pyttsx3` worker speaks sentences as they complete.
- **Session logging** – conversations saved to `log.json` with metadata.
- **Unit tests** – TDD-friendly tests for personas, logging, and speech.

## Installation

Requires Python 3.11+ and [Poetry](https://python-poetry.org/). PortAudio is needed for speech recognition.

```sh
git clone https://github.com/sebastianlam/drunkgpt.git
cd drunkgpt
poetry install
export OPENAI_API_KEY=<your_key>
poetry run python main.py
```

For convenience, `setup.sh` automates dependency setup on Linux and macOS.

## Development

Run the test suite before committing changes.

```sh
pytest -q
```

## Project Layout

```
main.py            – CLI entry point
persona.py         – persona management helpers
speech.py          – async TTS queue
logging_utils.py   – session logging utilities
personas.json      – persona definitions
tests/             – unit tests
```

## Next Steps

- Expand documentation for API usage and configuration.
- Improve cross-platform speech recognition support.
