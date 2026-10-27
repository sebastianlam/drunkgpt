import asyncio
import queue

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
        self.engine.setProperty("rate", rate)

    def _speak_blocking(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()

    async def speak(self, text: str) -> None:
        if text:
            await asyncio.to_thread(self._speak_blocking, text)


async def tts_worker(speech_queue: queue.Queue, rate: int = 200) -> None:
    """Speak items from a thread-safe queue until a None sentinel arrives.

    The chat loop runs on the main thread and can ``put`` sentences safely.
    When the engine cannot start, items are discarded so ``Queue.join`` still
    returns and text chat keeps working.
    """
    engine = None
    try:
        engine = SpeechEngine(rate)
    except RuntimeError as exc:
        print(f"Speech disabled: {exc}")

    while True:
        text = await asyncio.to_thread(speech_queue.get)
        try:
            if text is None:
                break
            if engine is not None and text:
                try:
                    await engine.speak(text)
                except Exception as exc:
                    print(f"Speech failed: {exc}")
        finally:
            speech_queue.task_done()
