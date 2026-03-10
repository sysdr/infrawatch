import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.registry import version_registry


class VersioningMiddleware(BaseHTTPMiddleware):
    VERSION_PATTERN = re.compile(r"^/api/(v\d+)/")

    async def dispatch(self, request: Request, call_next) -> Response:
        version = self._detect_version(request)
        request.state.api_version = version
        response = await call_next(request)
        if version:
            response.headers["X-API-Version"] = version
        return response

    def _detect_version(self, request: Request) -> str:
        match = self.VERSION_PATTERN.match(request.url.path)
        if match:
            return match.group(1)
        header = request.headers.get("X-API-Version", "")
        if header:
            return header if header.startswith("v") else f"v{header}"
        accept = request.headers.get("Accept", "")
        if "version=" in accept:
            try:
                ver = accept.split("version=")[1].split(";")[0].strip()
                return ver if ver.startswith("v") else f"v{ver}"
            except Exception:
                pass
        return "v2"


class DeprecationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        version = getattr(request.state, "api_version", None)
        if not version:
            return response
        status = version_registry.get_version_status(version)
        if status == "deprecated":
            v_info = version_registry.get_version(version)
            if v_info:
                if v_info.get("sunset_date"):
                    response.headers["Sunset"] = v_info["sunset_date"]
                if v_info.get("deprecation_date"):
                    response.headers["Deprecation"] = v_info["deprecation_date"]
                response.headers["Link"] = (
                    f'</api/migration/{version}/v2>; rel="successor-version", '
                    f'</api/versions/{version}>; rel="deprecation"'
                )
                response.headers["X-Deprecation-Notice"] = (
                    f"API {version} is deprecated. Please migrate to v2. "
                    f"Sunset: {v_info.get('sunset_date', 'TBD')}"
                )
        return response
