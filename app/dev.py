"""Run the development server and open the broadcast overlay once it is ready."""

import logging
import threading
import time
import webbrowser
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

import uvicorn

URL = "http://127.0.0.1:8000"
logger = logging.getLogger("uvicorn.error")


def open_when_ready(stopped: threading.Event) -> None:
    opener = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + 30
    while not stopped.is_set() and time.monotonic() < deadline:
        try:
            with opener.open(f"{URL}/health", timeout=1) as response:
                ready = response.status == 200
        except URLError, OSError:
            ready = False
        if ready and not stopped.is_set():
            try:
                if not webbrowser.open_new_tab(f"{URL}/overlay"):
                    logger.warning("Could not open a browser. Open %s/overlay manually.", URL)
            except webbrowser.Error:
                logger.warning("Could not open a browser. Open %s/overlay manually.", URL)
            return
        stopped.wait(0.25)
    if not stopped.is_set():
        logger.warning("Browser launch timed out. Open %s/overlay when ready.", URL)


def main() -> None:
    stopped = threading.Event()
    threading.Thread(target=open_when_ready, args=(stopped,), daemon=True).start()
    try:
        uvicorn.run("app.main:app", reload=True, host="127.0.0.1", port=8000)
    finally:
        stopped.set()


if __name__ == "__main__":
    main()
