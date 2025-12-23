import time

import schedule

from ..crawler_runner import run_all_sources


def start_scheduler():
    schedule.every(1).minutes.do(run_all_sources)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_scheduler()
