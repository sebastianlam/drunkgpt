import asyncio

# pyttsx3 may be unavailable in minimal test environments; import lazily
try:  # pragma: no cover - import guard is simple
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - handled in SpeechEngine
    pyttsx3 = None  # type: ignore

class SpeechEngine:
    def __init__(self, rate: int = 200):
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 is required for TTS but is not installed")
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            raise RuntimeError(f"TTS initialization failed: {e}") from e
        self.engine.setProperty('rate', rate)

    def _speak_blocking(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()

    async def speak(self, text: str) -> None:
        if text:
            await asyncio.to_thread(self._speak_blocking, text)

async def tts_worker(queue: asyncio.Queue, rate: int = 200) -> None:
    """Asynchronously process text from queue and speak it."""
    engine = SpeechEngine(rate)
    while True:
        text = await queue.get()
        if text is None:
            queue.task_done()
            break
        try:
            await engine.speak(text)
        finally:
            queue.task_done()
