import asyncio
import queue
import types

import speech


class DummyEngine:
    def __init__(self):
        self.spoken = []

    def setProperty(self, name, value):
        pass

    def say(self, text):
        self.spoken.append(text)

    def runAndWait(self):
        pass


def test_tts_worker_drains_queue():
    dummy_engine = DummyEngine()
    speech.pyttsx3 = types.SimpleNamespace(init=lambda: dummy_engine)
    speech_queue = queue.Queue()
    speech_queue.put("hello")
    speech_queue.put("world")
    speech_queue.put(None)
    asyncio.run(speech.tts_worker(speech_queue, rate=100))
    assert dummy_engine.spoken == ["hello", "world"]
    assert speech_queue.empty()


def test_tts_worker_discards_text_when_engine_missing():
    speech.pyttsx3 = None
    speech_queue = queue.Queue()
    speech_queue.put("hello")
    speech_queue.put(None)
    asyncio.run(speech.tts_worker(speech_queue, rate=100))
    assert speech_queue.empty()
