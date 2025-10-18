# deltica/backend/middleware/logging_middleware.py

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для автоматического логирования всех HTTP запросов.

    Логирует:
    - Метод и путь запроса
    - Статус код ответа
    - Время выполнения
    - IP адрес клиента
    - Пользователь (если аутентифицирован)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Засекаем время начала
        start_time = time.time()

        # Получаем IP адрес
        client_ip = request.client.host if request.client else "unknown"

        # Обрабатываем запрос
        response: Response = await call_next(request)

        # Вычисляем длительность
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Определяем пользователя (если есть в state)
        user = getattr(request.state, "user", None)
        username = user.username if user else "anonymous"

        # Логируем запрос
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            extra={
                "event": "http_request",
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "ip": client_ip,
                "user": username,
            }
        )

        return response
