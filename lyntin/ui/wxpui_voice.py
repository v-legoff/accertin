import time

import pyTTS


MINIMAL_PLAYING_TIME = 1 # in seconds
TTS_TIMEOUT = .1 # in seconds

_tts = pyTTS.Create()
_tts_previous_start_time = 0

def _tts_is_speaking():
    # The TTS doesn't always start speaking at once, but we don't want to wait.
    # So we consider that the TTS is speaking during the first milliseconds,
    # even if _tts.IsSpeaking() returns False.
    return _tts.IsSpeaking() or time.time() < _tts_previous_start_time + TTS_TIMEOUT

def _tts_speak(text):
    global _tts_previous_start_time
    _tts.Speak(text, pyTTS.tts_async, pyTTS.tts_purge_before_speak)
    _tts.Resume() # in case Pause() has been used
    _tts_previous_start_time = time.time()

def _tts_stop():
    global _tts_previous_start_time
    _tts.Pause() # Stop() might take ,too much time
    _tts_previous_start_time = 0


class _Message:

    said = False

    def __init__(self, text):
        self.text = text

    def play(self):
        """Start saying the message."""
        _tts_speak(self.text)
        self._start_time = time.time()

    def stop(self):
        """Stop saying the message."""
        _tts_stop()
        self._stop_time = time.time()
        if time.time() >= self._start_time + MINIMAL_PLAYING_TIME:
            self.said = True


class _MessageQueue:

    _current = None
    _playing_item = False
    _history = False

    def __init__(self):
        self._msgs = []

    def alert(self, text):
        """Say now and entirely. Remember it as read."""
        m = _Message(text)
        m.play()
        while _tts_is_speaking():
            time.sleep(.1)
        m.said = True
        self._msgs.append(m)

    def urgent(self, text):
        """Start saying text now, remember it as read anyway, and leave the rest of the queue unchanged."""
        self._stop_current_if_needed()
        m = _Message(text)
        m.said = True
        self._msgs.append(m)
        self._current = m
        m.play()

    def info(self, text):
        """Append a message to the queue. Say it when the time has come."""
        self._msgs.append(_Message(text))
        self.update()

    def _stop_current_if_needed(self):
        if not self._playing_item and self._current is not None:
            self._current.stop()

    def item(self, text):
##        self.urgent(text)
##        return
        """Say the message immediately and don't remember it."""
        self._stop_current_if_needed()
        _tts_speak(text)
        self._playing_item = True

    def _next_unsaid_or_said(self):
        if self._current in self._msgs:
            try:
                return self._msgs[self._msgs.index(self._current) + 1]
            except IndexError:
                return

    def _next_msg(self):
        if self._history:
            return self._next_unsaid_or_said()
        for m in self._msgs:
            if not m.said:
                return m

    def update(self):
        """Must be called often to make sure that everything is said."""
        if not _tts_is_speaking():
            if self._playing_item:
                self._playing_item = False
            elif self._current is not None:
                self._current.said = True
            self._current = self._next_msg()
            if self._current is not None:
                self._current.play()
            else:
                self._history = False

    def must_talk(self):
        """Return True if at least a message or an item is to be said."""
        return self._playing_item or self._current is not None

    def previous(self):
        """Go to the previous message."""
        self._stop_current_if_needed()
        self._history = True
        if self._current in self._msgs:
            i = self._msgs.index(self._current)
            if i > 0:
                self._current = self._msgs[i - 1]
        elif self._msgs:
            self._current = self._msgs[-1]
        if self._current is not None:
            self._current.play()

    def next(self):
        """Go to the next message (if the current message has been said)."""
        if self._current is not None and not self._current.said:
            return
        self._stop_current_if_needed()
        self._current = self._next_unsaid_or_said()
        if self._current is not None:
            self._current.play()

    def flush(self):
        """Stop current queued message and mark all as said."""
        for m in self._msgs:
            m.said = True
        self._history = False
        self._stop_current_if_needed()


voice = _MessageQueue()
