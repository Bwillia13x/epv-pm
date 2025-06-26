import asyncio
from functools import partial
from typing import Callable, TypeVar, Any

T = TypeVar("T")


def to_async(func: Callable[..., T], /, *args: Any, **kwargs: Any) -> "asyncio.Future[T]":
    """Execute *func* in default thread pool returning awaitable result."""
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, partial(func, *args, **kwargs))