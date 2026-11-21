import sys
import os
from pathlib import Path

# Ensure the project root is in sys.path so we can import app.* modules
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import time
import os
import signal
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict
from app.jobs import queue
from app.observability import log_event

HANDLERS = {
    'discovery': lambda p: {'message': 'Discovery complete'},
    'inventory-refresh': lambda p: {'message': 'Inventory refreshed'},
    'diagnostic': lambda p: {'message': 'Diagnostics complete'},
    'test-fail': lambda p: (_ for _ in ()).throw(RuntimeError('Synthetic failure')),
}

def get_client_ip(request: Any = None):
    return "unknown"

_stop_requested = False

def _handle_signal(signum, frame):
    global _stop_requested
    _stop_requested = True

def process_one():
    j = queue.claim()
    if not j:
        return None
    try:
        if j['cancel_requested']:
            return queue.complete(j['id'], None)
        log_event(user='worker', action='job_start', resource=j['id'], details={'kind': j['kind'], 'priority': j['priority'], 'metadata': j['metadata']})
        result = HANDLERS[j['kind']](j['payload'])
        return queue.complete(j['id'], result)
    except Exception as e:
        return queue.fail(j['id'], e)

def run():
    global _stop_requested
    _stop_requested = False
    worker_count = int(os.getenv('WORKER_COUNT', '1'))
    executor = ThreadPoolExecutor(max_workers=worker_count)

    def _handle_signal(signum, frame):
        global _stop_requested
        _stop_requested = True

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    while not _stop_requested:
        # Submit job to thread pool
        future = executor.submit(process_one)
        # Wait for job to finish
        try:
            result = future.result(timeout=10)  # timeout in seconds
            if result is None:
                # No job available, sleep a bit
                time.sleep(1)
        except Exception:
            # If exception occurs, continue
            pass

        # Check if stop was requested
        if _stop_requested:
            break

    executor.shutdown(wait=False)

if __name__ == '__main__':
    run()

def get_status():
    with queue.lock:
        return {
            'total_jobs': len(queue.jobs),
            'ready_jobs': len(queue.ready),
            'running_jobs': sum(1 for j in queue.jobs.values() if j.get('status') == 'running'),
            'succeeded': sum(1 for j in queue.jobs.values() if j.get('status') == 'succeeded'),
            'failed': sum(1 for j in queue.jobs.values() if j.get('status') == 'failed'),
            'dead_letter': sum(1 for j in queue.jobs.values() if j.get('status') == 'dead_letter'),
            'cancelled': sum(1 for j in queue.jobs.values() if j.get('status') == 'cancelled'),
            'queued': sum(1 for j in queue.jobs.values() if j.get('status') == 'queued'),
            'worker_count': int(os.getenv('WORKER_COUNT', '1'))
        }