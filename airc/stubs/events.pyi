"""
    Events stubs for the AIRC module
"""

from typing import Dict, List
from .server import TwitchServer
from .utils import IRCPrefix

numeric: Dict[str, str] = ...

codes: Dict[str, str] = ...

generated: List[str] = ...

protocol: List[str] = ...

twitch: List[str] = ...

all: List[str] = ...

class Event:

    __slots__ = ("server", "type", "target", "arguments", "prefix", "tags")

    server: TwitchServer
    type: str
    target: str
    arguments: List[str]
    prefix: IRCPrefix
    tags: Dict[str, str]

    def __init__(self, server: TwitchServer, type: str, arguments: List[str], prefix: str = ..., tags: Dict[str, str] = ...) -> None: ...

    def __str__(self) -> str: ...