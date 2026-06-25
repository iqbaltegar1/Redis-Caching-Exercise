import argparse
import os
import statistics
import sys
import time

import requests

DEFAULT_BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
DEFAULT_COURSE_ID = int(os.environ.get('COURSE_ID', '1'))
DEFAULT_ITERATIONS = 50
DEFAULT_REDIS_URL = os.environ.get('REDIS_CACHE_URL', 'redis://127.0.0.1:6379/1')

try:
    import redis
except ImportError:
    redis = None


def parse_args():
    parser = argparse.ArgumentParser(
        description='Benchmark Simple LMS Redis caching performance.'
    )
    parser.add_argument(
        '--base-url', default=DEFAULT_BASE_URL,
        help='Base URL for the Django API (default: http://127.0.0.1:8000)'
    )
    parser.add_argument(
        '--course-id', type=int, default=DEFAULT_COURSE_ID,
        help='Course ID to use for course detail benchmark.'
    )
    parser.add_argument(
        '--iterations', type=int, default=DEFAULT_ITERATIONS,
        help='Number of requests per endpoint.'
    )
    parser.add_argument(
        '--flush-cache', action='store_true',
        help='Flush Redis cache database before benchmarking.'
    )
    parser.add_argument(
        '--redis-url', default=DEFAULT_REDIS_URL,
        help='Redis cache URL to flush when using --flush-cache.'
    )
    return parser.parse_args()


def flush_cache(redis_url: str):
    if redis is None:
        print('redis package is not installed. Cannot flush cache.')
        return

    print(f'Flushing Redis cache at {redis_url}...')
    client = redis.from_url(redis_url, decode_responses=True)
    client.flushdb()
    print('Redis cache flushed.')


def measure_request(method, url, session, json_data=None):
    start = time.time()
    response = session.request(method, url, json=json_data)
    elapsed = (time.time() - start) * 1000
    if not response.ok:
        raise RuntimeError(f'HTTP {response.status_code} from {url}')
    return elapsed


def benchmark_endpoint(label, method, url, session, iterations, json_data=None):
    print(f'Benchmarking {label} ({iterations} requests)...')
    times = []
    for _ in range(iterations):
        elapsed = measure_request(method, url, session, json_data=json_data)
        times.append(elapsed)
    return times


def summarize(label, times):
    avg = statistics.mean(times)
    mn = min(times)
    mx = max(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0.0
    print(f'\n{label}')
    print(f'  Count      : {len(times)}')
    print(f'  Avg        : {avg:.2f} ms')
    print(f'  Min        : {mn:.2f} ms')
    print(f'  Max        : {mx:.2f} ms')
    print(f'  Std Dev    : {stdev:.2f} ms')


def main():
    args = parse_args()
    base_url = args.base_url.rstrip('/')
    course_id = args.course_id
    iterations = args.iterations

    if args.flush_cache:
        flush_cache(args.redis_url)

    session = requests.Session()

    print('\n== Simple LMS Redis Benchmark ==')
    print(f'Base URL: {base_url}')
    print(f'Course ID: {course_id}')
    print(f'Iterations: {iterations}')

    all_courses_url = f'{base_url}/api/v1/courses'
    course_detail_url = f'{base_url}/api/v1/courses/{course_id}'

    print('\n-- Cold cache measurement (first request) --')
    first_course = measure_request('GET', all_courses_url, session)
    first_detail = measure_request('GET', course_detail_url, session)
    print(f'  First GET /api/v1/courses: {first_course:.2f} ms')
    print(f'  First GET /api/v1/courses/{course_id}: {first_detail:.2f} ms')

    print('\n-- Warm cache measurement --')
    courses_times = benchmark_endpoint('GET /api/v1/courses', 'GET', all_courses_url, session, iterations)
    detail_times = benchmark_endpoint(f'GET /api/v1/courses/{course_id}', 'GET', course_detail_url, session, iterations)

    summarize('GET /api/v1/courses', courses_times)
    summarize(f'GET /api/v1/courses/{course_id}', detail_times)

    visit_url = f'{base_url}/api/v1/courses/{course_id}/visit/'
    visit_times = benchmark_endpoint(f'POST /api/v1/courses/{course_id}/visit/', 'POST', visit_url, session, 10)
    summarize(f'POST /api/v1/courses/{course_id}/visit/', visit_times)

    popular_url = f'{base_url}/api/v1/courses/popular/'
    popular_times = benchmark_endpoint('GET /api/v1/courses/popular/', 'GET', popular_url, session, 10)
    summarize('GET /api/v1/courses/popular/', popular_times)

    print('\nBenchmark completed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
