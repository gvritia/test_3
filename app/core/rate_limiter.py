"""Простейший in-memory rate limiter для задания 6.5."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """Ограничивает число запросов за фиксированный интервал времени.

    Механика простая:
    1. Для каждого IP и пути храним список временных меток запросов.
    2. Перед новым запросом вычищаем старые записи.
    3. Если лимит уже исчерпан, возвращаем 429.
    """

    def __init__(self, max_requests: int, period_seconds: int) -> None:
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{client_ip}"
        now = time.time()

        with self._lock:
            # Оставляем только запросы, которые попадают в текущее окно времени.
            request_times = self._requests[key]
            self._requests[key] = [
                timestamp
                for timestamp in request_times
                if now - timestamp < self.period_seconds
            ]

            if len(self._requests[key]) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )

            # Если лимит не превышен, регистрируем текущий запрос.
            self._requests[key].append(now)
