import os
import shutil
import subprocess
import time

OUT_FILE = 'redis_monitor.txt'
DURATION = int(os.environ.get('REDIS_MONITOR_DURATION', '15'))
DOCKER_CONTAINER = os.environ.get('REDIS_CONTAINER_NAME', 'nosql-redis-redis-1')


def generate_redis_traffic():
    try:
        import redis
        client = redis.from_url('redis://127.0.0.1:6379/1', decode_responses=True)
        for i in range(5):
            client.set(f'monitor_test_key_{i}', f'value_{i}')
            client.get(f'monitor_test_key_{i}')
            client.incr('monitor_test_counter')
            time.sleep(1)
    except Exception:
        pass


def monitor_with_docker():
    if shutil.which('docker') is None:
        return False

    try:
        subprocess.run(
            ['docker', 'exec', DOCKER_CONTAINER, 'command', '-v', 'timeout'],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return False

    monitor_cmd = [
        'docker', 'exec', DOCKER_CONTAINER,
        'sh', '-c', f'timeout {DURATION} redis-cli MONITOR'
    ]

    traffic_thread = threading.Thread(target=generate_redis_traffic, daemon=True)
    traffic_thread.start()

    with open(OUT_FILE, 'w', encoding='utf-8') as output_file:
        proc = subprocess.Popen(monitor_cmd, stdout=output_file, stderr=subprocess.STDOUT)
        try:
            proc.wait(timeout=DURATION + 5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return proc.returncode in (0, 124)


def monitor_with_redis_client():
    try:
        import redis
    except ImportError:
        return False

    try:
        client = redis.from_url(
            'redis://127.0.0.1:6379/1',
            decode_responses=True,
            socket_timeout=DURATION + 5,
            retry_on_timeout=True,
        )
        monitor = client.monitor()

        with open(OUT_FILE, 'w', encoding='utf-8') as output_file:
            start = time.time()
            while time.time() - start < DURATION:
                try:
                    cmd = next(monitor.listen())
                except redis.exceptions.TimeoutError:
                    continue
                if cmd is None:
                    continue
                output_file.write(f"{cmd}\n")
                output_file.flush()
    except Exception:
        return False

    return True


if __name__ == '__main__':
    print(f'Attempting Redis MONITOR capture for {DURATION} seconds...')
    if monitor_with_docker():
        print(f'Done. Output saved to {OUT_FILE} using Docker monitor.')
    elif monitor_with_redis_client():
        print(f'Done. Output saved to {OUT_FILE} using redis-py client monitor.')
    else:
        print('Failed to capture Redis MONITOR output. Ensure Docker or redis-py is available.')
