import asyncio
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
    queue = asyncio.Queue()
    queue.put_nowait("hello")
    queue.put_nowait("world")
    queue.put_nowait(None)
    async def run_worker():
        await speech.tts_worker(queue, rate=100)
    asyncio.run(run_worker())
    assert dummy_engine.spoken == ["hello", "world"]
    assert queue.empty()
