"""
    AIRC utils stub file
"""

from typing import Pattern, Union, Callable, List, Any
from .events import Event


class Cooldown:

    __slots__ = ("per", "time", "name", "start", "count")

    per: int
    time: int
    name: str
    start: float
    count: int

    def __init__(self, per: int, time: int, name: str = ...) -> None: ...

    def set_per(self, per: int) -> None: ...

    def set_time(self, time: int) -> None: ...

    def can_run(self) -> bool: ...

class LineBuffer:

    __slots__ = ("data",)

    _line_sep: Pattern = ...

    data: bytes

    def __init__(self) -> None: ...

    def feed(self, line: Union[bytes, str]) -> None: ...

    def lines(self) -> iter: ...

    def __iter__(self) -> iter: ...

    def __len__(self) -> int: ...

class SortedHandler:

    __slots__ = ("handler", "priority")

    handler: Callable[[Event], None]
    priority: int

    def __init__(self, handler: Callable[[Event], None], priority: int = ...) -> None: ...

    async def __call__(self, event: Event) -> None: ...

    def __lt__(self, other: SortedHandler) -> bool: ...

    def __gt__(self, other: SortedHandler) -> bool: ...

class IRCPrefix(str):

    __slots__ = ("nick", "user", "host")

    nick: str
    user: str
    host: str

    def __new__(cls, prefix: Any) -> IRCPrefix: ...

    def __init__(self,prefix: str) -> None: ...

def insort(li: List, o: Any, lo: int = ..., hi: int = ...) -> None: ...
