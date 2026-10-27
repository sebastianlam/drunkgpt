import types

import pytest

from chat import (
    ChatSession,
    ask_rate,
    chat_loop,
    choose_model,
    classify_command,
    is_selectable_model,
    list_ollama_model_ids,
    make_complete,
    menu_from_ids,
    ollama_deltas,
    openai_deltas,
    render_stream,
    resolve_model_choice,
    transcription_text,
)


class APIError(Exception):
    pass


def _session(inputs, **overrides):
    remaining = iter(inputs)

    def read_line(prompt=""):
        try:
            return next(remaining)
        except StopIteration as exc:
            raise AssertionError(f"unexpected prompt: {prompt}") from exc

    spoken = []
    written = []
    logs = []
    session = ChatSession(
        context=[{"role": "system", "content": "system-a"}],
        model="gpt-4o",
        agent="A",
        personas={"A": "system-a", "B": "system-b"},
        persona_options={1: "A", 2: "B"},
        voice=False,
        log_file="log.json",
        start_time="start",
        input_fn=read_line,
        complete=lambda model, messages: iter(["Hi", "."]),
        enqueue=spoken.append,
        clear_speech=lambda: spoken.append("<cleared>"),
        wait_for_speech=lambda: None,
        log_fn=lambda *args: logs.append(args),
        time_fn=lambda: "later",
        write=written.append,
        transcribe_fn=None,
    )
    for key, value in overrides.items():
        setattr(session, key, value)
    return session, spoken, written, logs


def test_classify_command_matches_exact_controls():
    assert classify_command("new") == "new"
    assert classify_command("Quit") == "quit"
    assert classify_command("") == "empty"
    assert classify_command(" ") == "skip"
    assert classify_command("new ") == "message"


def test_render_stream_speaks_boundaries_and_trailing_fragment():
    spoken = []
    written = []
    text = render_stream(["Hello", ".", " there"], spoken.append, written.append)
    assert text == "Hello. there"
    assert written == ["Hello", ".", " there"]
    assert spoken == ["Hello.", " there"]


def test_render_stream_flushes_on_empty_delta():
    spoken = []
    text = render_stream(["Hello", None], spoken.append, lambda _text: None)
    assert text == "Hello"
    assert spoken == ["Hello"]


def test_model_menu_hides_non_chat_models_and_keeps_local_ids():
    ids = [
        "whisper-1",
        "text-embedding-3-large",
        "gpt-4o",
        "o3-mini",
        "dall-e-3",
        "tts-1",
        "ollama:llama3.2",
        "gpt-4o-audio-preview",
    ]
    assert [model_id for model_id in ids if is_selectable_model(model_id)] == [
        "gpt-4o",
        "o3-mini",
        "ollama:llama3.2",
    ]
    assert menu_from_ids(ids) == {1: "gpt-4o", 2: "o3-mini", 3: "ollama:llama3.2"}


def test_resolve_model_choice_accepts_menu_index_and_ollama_prefix():
    models = {1: "gpt-4o"}
    assert resolve_model_choice("1", models) == "gpt-4o"
    assert resolve_model_choice("  Ollama:llama3.2 ", models) == "ollama:llama3.2"
    assert resolve_model_choice("ollama:", models) is None
    assert resolve_model_choice("nope", models) is None


def test_choose_model_accepts_a_typed_id_when_nothing_was_discovered():
    assert choose_model(lambda _prompt: "gpt-4o", {}) == "gpt-4o"


def test_ask_rate_retries_then_defaults():
    answers = iter(["fast", ""])
    assert ask_rate(lambda _prompt: next(answers)) == 200
    assert ask_rate(lambda _prompt: "180") == 180


def test_chat_loop_streams_a_reply_and_logs_on_quit():
    session, spoken, written, logs = _session(["Hello", "quit"])
    chat_loop(session)
    assert written == ["Hi", "."]
    assert spoken == ["Hi."]
    assert session.context[-1] == {"role": "assistant", "content": "Hi."}
    assert logs[-1][1] == session.context
    assert logs[-1][3] == "gpt-4o"


def test_chat_loop_ignores_blank_input_and_skips_speech():
    session, spoken, _written, logs = _session(["", " ", "quit"])
    chat_loop(session)
    assert spoken == ["<cleared>"]
    assert len(logs) == 1


def test_chat_loop_new_saves_the_old_persona_and_switches():
    session, _spoken, _written, logs = _session(["new", "2", "quit"])
    chat_loop(session)
    assert session.agent == "B"
    assert session.context == [{"role": "system", "content": "system-b"}]
    assert logs[0][1] == [{"role": "system", "content": "system-a"}]
    assert session.start_time == "later"


def test_chat_loop_logs_and_stops_when_the_provider_fails():
    def fail(model, messages):
        raise APIError("down")
        yield  # pragma: no cover - makes this a generator

    session, _spoken, _written, logs = _session(["Hello"], complete=fail)
    chat_loop(session)
    assert len(logs) == 1
    assert session.context[-1]["role"] == "user"


def test_chat_loop_dictation_falls_back_to_typing():
    def fail_mic():
        raise OSError("no microphone")

    def echo(_model, messages):
        yield messages[-1]["content"]
        yield "."

    answers = iter(["typed instead", "quit"])
    session, spoken, _written, _logs = _session(
        [],
        voice=True,
        transcribe_fn=fail_mic,
        input_fn=lambda _prompt: next(answers),
        complete=echo,
    )
    chat_loop(session)
    assert spoken == ["typed instead."]
    assert session.context[1]["content"] == "typed instead"


def test_chat_loop_dictation_enqueues_a_cross_platform_cue():
    said = iter(["from the mic", "quit"])

    def unused(_prompt):
        raise AssertionError("typed input unused")

    session, spoken, _written, _logs = _session(
        [],
        voice=True,
        transcribe_fn=lambda: next(said),
        input_fn=unused,
    )
    chat_loop(session)
    assert spoken[0] == "hmm..."
    assert spoken.count("hmm...") == 1
    assert session.context[1]["content"] == "from the mic"


def test_openai_deltas_use_the_v1_client():
    def chunk(text):
        delta = types.SimpleNamespace(content=text)
        choice = types.SimpleNamespace(delta=delta)
        return types.SimpleNamespace(choices=[choice])

    class Completions:
        def create(self, model, messages, stream):
            assert model == "gpt-4o"
            assert stream is True
            assert messages[0]["role"] == "user"
            return [chunk("A"), chunk(None)]

    client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=Completions()))
    assert list(openai_deltas(client, "gpt-4o", [{"role": "user", "content": "hi"}])) == [
        "A",
        None,
    ]


def test_ollama_discovery_and_streaming():
    class Remote:
        def list(self):
            return {"models": [{"model": "llama3.2"}, {"name": "ignored"}]}

        def chat(self, model, messages, stream):
            assert model == "llama3.2"
            assert stream is True
            yield {"message": {"content": "Hi"}}

    assert list_ollama_model_ids(lambda: Remote()) == ["ollama:llama3.2", "ollama:ignored"]
    assert list(ollama_deltas("llama3.2", [], factory=lambda: Remote())) == ["Hi", None]

    complete = make_complete(None, ollama_factory=lambda: Remote())
    assert list(complete("ollama:llama3.2", [])) == ["Hi", None]
    with pytest.raises(RuntimeError):
        list(complete("gpt-4o", []))


def test_transcription_uploads_wav_bytes_and_returns_text():
    class Audio:
        def get_wav_data(self):
            return b"RIFFfake"

    class Transcriptions:
        def create(self, model, file):
            assert model == "whisper-1"
            name, handle, mime = file
            assert name == "speech.wav"
            assert handle.read() == b"RIFFfake"
            assert mime == "audio/wav"
            return types.SimpleNamespace(text="hello there")

    client = types.SimpleNamespace(audio=types.SimpleNamespace(transcriptions=Transcriptions()))
    assert transcription_text(client, Audio()) == "hello there"


def test_main_import_does_not_require_an_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import importlib
    import main

    importlib.reload(main)
    assert callable(main.main)
