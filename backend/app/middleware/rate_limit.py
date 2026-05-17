import logging
import time
import threading

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.exceptions import RateLimitError

logger = logging.getLogger(__name__)


class TokenBucket:
    def __init__(self, rate: int):
        self.rate = rate
        self.tokens = rate
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def consume(self) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / 60.0))
            self.last_refill = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, key: str) -> TokenBucket:
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(settings.RATE_LIMIT_PER_MINUTE)
            return self._buckets[key]

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        bucket = self._get_bucket(client_ip)
        if not bucket.consume():
            raise RateLimitError()

        return await call_next(request)
