from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

RATE_LIMIT = 60
time_window = 60

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting in DEBUG to avoid blocking local tests/benchmarks
        if not settings.DEBUG and request.path.startswith('/api/'):
            client_ip = self._get_client_ip(request)
            key = f"rate_limit:{client_ip}"
            request_count = cache.get(key)

            if request_count is None:
                cache.add(key, 1, time_window)
                request_count = 1
            else:
                if request_count >= RATE_LIMIT:
                    return JsonResponse(
                        {'detail': 'Rate limit exceeded. Maksimum 60 request per menit.'},
                        status=429
                    )
                cache.incr(key)

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
