import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)

LOG_FILE = os.path.join(
    LOG_DIR,
    "activity.log"
)


def log_event(event):

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a") as file:

        file.write(
            f"[{timestamp}] {event}\n"
        )