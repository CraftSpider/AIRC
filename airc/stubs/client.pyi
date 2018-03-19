"""
    AIRC Client file stubs
"""

import asyncio
import abc

from typing import List, Any, Dict, Optional
from .master import ServerMaster
from .server import TwitchServer
from .events import Event
from .enums import UserType


async def empty_handler(event: Event) -> None: ...

def empty_handler_sync(event: Event) -> None: ...

class TwitchClient:

    master: ServerMaster
    server: TwitchServer
    membership: bool
    commands: bool
    tags: bool
    channels: List[TwitchChannel]

    def __init__(self, user_type: UserType = ..., loop: asyncio.AbstractEventLoop = ...) -> None: ...

    def run(self, uri: str, username: str, password: str) -> None: ...

    def get_channel(self, name: str) -> Optional[TwitchChannel]: ...

    def create_channel(self, name: str) -> TwitchChannel: ...

    async def _dispatch(self, event) -> None: ...

    def handle_cap(self, event: Event) -> None: ...

    def handle_join(self, event: Event) -> None: ...

    def handle_mode(self, event: Event) -> None: ...

    def handle_namreply(self, event: Event) -> None: ...

    def handle_part(self, event: Event) -> None: ...

    def handle_privmsg(self, event: Event) -> None: ...

    def handle_roomstate(self, event: Event) -> None: ...

    def handle_userstate(self, event: Event) -> None: ...

class Messageable:

    __slots__ = ()

    @abc.abstractmethod
    async def send(self, message: Any) -> None: ...

class TwitchChannel(Messageable):

    __slots__ = ("id", "name", "lang", "emote_only", "follower_only", "mercury", "r9k", "rituals", "slow", "sub_only",
                 "users", "server")

    id: int
    name: str
    lang: Optional[str]
    emote_only: bool
    follower_only: bool
    mercury: bool
    r9k: bool
    rituals: bool
    slow: int
    sub_only: bool
    users: List[TwitchUser]
    server: TwitchServer

    def __init__(self, name: str, server: TwitchServer) -> None: ...

    def __eq__(self, other: Any) -> bool: ...

    @property
    def me(self) -> TwitchUser: return

    def set_state(self, tags: Dict[str, str]) -> None: ...

    def create_user(self, name: str) -> TwitchUser: ...

    def get_user(self, name: str) -> Optional[TwitchUser]: ...

    def remove_user(self, name: str) -> None: ...

    async def send(self, message: Any) -> None: ...

def _process_badges(tags: str) -> Dict[str, str]: ...

class TwitchUser(Messageable):

    __slots__ = ("id", "name", "display_name", "turbo", "partner", "mod", "global_mod", "admin", "staff", "broadcaster",
                 "subscriber", "color", "badges", "sub_length", "bit_level", "server", "channel")

    id: int
    name: str
    display_name: str
    turbo: bool
    partner: bool
    mod: bool
    global_mod: bool
    admin: bool
    staff: bool
    broadcaster: bool
    subscriber: bool
    color: str
    badges: Dict[str, int]
    sub_length: int
    bit_level: int
    server: TwitchServer
    channel: TwitchChannel

    def __init__(self, name: str, channel: TwitchChannel, server: TwitchServer) -> None: ...

    def set_state(self, tags: Dict[str, str]) -> None: ...

    def set_mode(self, mode: str) -> None: ...

    async def send(self, message: Any) -> None: ...

    async def timeout(self, time: int) -> None: ...

    async def ban(self) -> None: ...

    async def unban(self) -> None: ...