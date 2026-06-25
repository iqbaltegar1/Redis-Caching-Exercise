import json
import os
import time

import redis
import requests

REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
CACHE_EXPIRE_SECONDS = 300


def get_redis_client():
    return redis.from_url(REDIS_URL, decode_responses=True)


def get_weather(city: str):
    """Simulasi API call yang lambat dengan Redis cache."""
    client = get_redis_client()
    cache_key = f"weather:{city.strip().lower()}"

    cached = client.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    # Simulasi API lambat
    time.sleep(2)

    try:
        response = requests.get(f"https://api.example.com/weather/{city}", timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception:
        data = {
            "city": city,
            "temperature": 30,
            "condition": "Sunny",
            "source": "simulated",
        }

    client.set(cache_key, json.dumps(data), ex=CACHE_EXPIRE_SECONDS)
    return data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Demo Redis caching untuk weather API")
    parser.add_argument("city", nargs="?", default="Jakarta", help="Nama kota")
    args = parser.parse_args()

    result = get_weather(args.city)
    print(result)
