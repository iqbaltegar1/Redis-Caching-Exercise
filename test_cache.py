import time

from weather_api import get_weather


def main():
    start = time.time()
    result1 = get_weather("Jakarta")
    time1 = time.time() - start
    print(f"First call: {time1:.2f}s")
    print(f"Result 1: {result1}\n")

    start = time.time()
    result2 = get_weather("Jakarta")
    time2 = time.time() - start
    print(f"Second call (cached): {time2:.2f}s")
    print(f"Result 2: {result2}\n")

    print("Note: Third call after 5 minutes should be slow again because cache expires after 300 detik.")
    print("Untuk demo cepat, hapus cache atau gunakan key yang berbeda jika ingin melihat panggilan baru.")


if __name__ == "__main__":
    main()
