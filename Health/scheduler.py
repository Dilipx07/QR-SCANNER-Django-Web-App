import logging
import os
import threading
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_started = False
_lock = threading.Lock()


def start_health_check_scheduler():
    global _started

    with _lock:
        if _started:
            return
        _started = True

    interval_seconds = int(os.getenv('HEALTH_CHECK_INTERVAL_SECONDS', '5'))
    target_url = _health_check_url()

    thread = threading.Thread(
        target=_run_scheduler,
        args=(target_url, interval_seconds),
        name='health-check-scheduler',
        daemon=True,
    )
    thread.start()
    logger.info('Health-check scheduler started for %s every %s seconds', target_url, interval_seconds)


def _run_scheduler(target_url, interval_seconds):
    while True:
        try:
            request = Request(target_url, headers={'User-Agent': 'qrscanner-health-scheduler/1.0'})
            with urlopen(request, timeout=5) as response:
                response.read()
                if response.status >= 400:
                    logger.warning('Health-check returned HTTP %s from %s', response.status, target_url)
        except (OSError, URLError) as exc:
            logger.warning('Health-check request failed for %s: %s', target_url, exc)
        time.sleep(interval_seconds)


def _health_check_url():
    configured_url = os.getenv('HEALTH_CHECK_URL')
    if configured_url:
        return configured_url

    render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    if render_hostname:
        return f'https://{render_hostname}/health/'

    port = os.getenv('PORT', '8000')
    return f'http://127.0.0.1:{port}/health/'
