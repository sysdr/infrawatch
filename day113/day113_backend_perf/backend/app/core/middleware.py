import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from prometheus_client import Histogram, Counter, Gauge
logger = logging.getLogger(__name__)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency in seconds", ["method", "route", "status"], buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0])
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP request count", ["method", "route", "status"])
ACTIVE_REQUESTS = Gauge("http_active_requests", "Currently active HTTP requests")
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        route = request.url.path
        method = request.method
        ACTIVE_REQUESTS.inc()
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception as exc:
            status = "500"
            raise exc
        finally:
            elapsed = time.perf_counter() - start
            REQUEST_LATENCY.labels(method=method, route=route, status=status).observe(elapsed)
            REQUEST_COUNT.labels(method=method, route=route, status=status).inc()
            ACTIVE_REQUESTS.dec()
        return response
