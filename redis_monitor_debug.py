import time
import threading
import redis

REDIS_URL = 'redis://127.0.0.1:6379/1'


def monitor_redis(duration=15):
    client = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=duration + 5, retry_on_timeout=True)
    monitor = client.monitor()
    print('monitor started')
    start = time.time()
    count = 0
    while time.time() - start < duration:
        try:
            cmd = next(monitor.listen())
        except redis.exceptions.TimeoutError:
            continue
        if cmd is None:
            continue
        count += 1
        print('cmd', count, cmd)
    print('monitor finished, count=', count)


def generate_traffic():
    time.sleep(1)
    client = redis.from_url(REDIS_URL, decode_responses=True)
    for i in range(10):
        client.set(f'test_mon_{i}', 'x')
        client.get(f'test_mon_{i}')
        client.incr('test_mon_counter')
        time.sleep(0.5)


if __name__ == '__main__':
    thr = threading.Thread(target=generate_traffic)
    thr.start()
    monitor_redis(10)
