"""Run slow work off the main thread without touching Tkinter from that thread."""

import queue
import threading
import tkinter as tk

POLL_MS = 50


def run_in_background(widget, work, on_done):
    """Run work() on a worker thread, then call on_done(result) on the Tk thread.

    Tkinter may only be used from the thread that runs the main loop, so the
    worker hands its result over through a queue that the main thread polls.

    If work() raises, on_done receives the exception instead of a result. If the
    widget has been destroyed in the meantime (the user moved to another screen
    or closed the app), on_done is not called at all.
    """
    results = queue.Queue()

    def worker():
        try:
            results.put(work())
        except Exception as exc:  # hand every failure back so the screen can recover
            results.put(exc)

    def poll():
        try:
            if not widget.winfo_exists():
                return
        except tk.TclError:
            return  # the whole app has been closed
        try:
            outcome = results.get_nowait()
        except queue.Empty:
            widget.after(POLL_MS, poll)
            return
        on_done(outcome)

    threading.Thread(target=worker, daemon=True).start()
    widget.after(POLL_MS, poll)
