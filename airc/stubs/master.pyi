"""
    AIRC master class stub file
"""

import asyncio

from typing import Coroutine, Any, List, Dict
from .events import Event
from .server import Server
from .utils import SortedHandler
from .server import TwitchServer
from .enums import UserType


class ServerMaster:

    __slots__ = ("loop", "user_type", "connections", "handlers")

    loop: asyncio.AbstractEventLoop
    user_type: str
    connections: List[Server]
    handlers: Dict[str, List[SortedHandler]]

    def __init__(self, user_type: UserType = ..., loop: asyncio.AbstractEventLoop = ...) -> None: ...

    def server(self, user_type: UserType = ...) -> TwitchServer: ...

    def add_global_handler(self, event: str, handler: type(Coroutine), priority: int = ...) -> None: ...

    def remove_global_handler(self, event: str, handler: type(Coroutine)) -> None: ...

    def run(self, *args: Any, **kwargs: Any) -> None: ...

    async def start(self, *args: Any, **kwargs: Any) -> None: ...

    async def _handle_event(self, event: Event) -> None: ...

async def _ponger(event: Event) -> None: ...