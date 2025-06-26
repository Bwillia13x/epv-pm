import httpx
from typing import Optional

_http_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    """Return a shared asynchronous HTTPX client.

    Lazily creates a singleton `httpx.AsyncClient` with sane defaults so that
    the application re-uses connections (keep-alive) instead of opening a new
    TCP connection for every request.  Call `close_client()` on shutdown."""

    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0))
    return _http_client


async def close_client() -> None:
    """Gracefully close the shared AsyncClient."""
    global _http_client
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None