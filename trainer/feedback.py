"""Real-time voice feedback using offline text-to-speech (pyttsx3)."""

from __future__ import annotations

import queue
import threading
import time
from typing import Dict


class VoiceCoach:
    """Speaks short coaching messages without blocking the video loop.

    Speech runs in a background thread. The same message is not repeated more
    often than ``cooldown`` seconds, and stale messages are dropped so the
    feedback always matches what the user is doing now.
    """

    def __init__(self, enabled: bool = True, cooldown: float = 4.0, rate: int = 170):
        self.enabled = enabled
        self.cooldown = cooldown
        self._rate = rate
        self._last_spoken: Dict[str, float] = {}
        self._queue: "queue.Queue[str | None]" = queue.Queue(maxsize=2)
        self._thread = None
        if enabled:
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def _worker(self) -> None:
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
        except Exception as exc:  # no audio device / missing driver
            print(f"[voice] disabled: {exc}")
            self.enabled = False
            return
        while True:
            text = self._queue.get()
            if text is None:
                break
            engine.say(text)
            engine.runAndWait()

    def say(self, text: str, force: bool = False) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        if not force and now - self._last_spoken.get(text, 0.0) < self.cooldown:
            return
        try:
            self._queue.put_nowait(text)
            self._last_spoken[text] = now
        except queue.Full:
            pass  # busy speaking; skip rather than lag behind

    def rep(self, count: int) -> None:
        self.say(str(count), force=True)

    def close(self) -> None:
        if self._thread:
            try:
                self._queue.put_nowait(None)
            except queue.Full:
                pass
