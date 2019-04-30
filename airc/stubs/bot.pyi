
from typing import List, Callable, Dict, Coroutine, Any, Union, Tuple
import logging
import asyncio
import inspect
from airc.events import Event
from airc.client import TwitchClient, TwitchChannel, TwitchUser, Messageable
from airc.server import TwitchServer, Cooldown
from airc.enums import UserType

log: logging.Logger


async def empty_handler(*args) -> None: ...

def empty_handler_sync(*args) -> None: ...

def _split_args(content: str) -> List[str]: ...

class TwitchBot(TwitchClient):

    prefix: str
    all_commands: Dict[Command]
    cogs: Dict
    _checks: List[Union[Coroutine, Callable]]


    def __init__(self, prefix: str, user_type: UserType = ..., loop: asyncio.AbstractEventLoop = ...) -> None: ...

    def add_check(self, predicate: Coroutine) -> None: ...

    def remove_check(self, predicate: Coroutine) -> None: ...

    def add_command(self, command: Command) -> None: ...

    def remove_command(self, name: str) -> Command: ...

    def command(self, *args, **kwargs) -> Callable: ...

    def add_cog(self, cog: Any) -> None: ...

    def remove_cog(self, name: str) -> None: ...

    def load_extension(self, name: str) -> None: ...

    def unload_extension(self, name: str) -> None: ...

    async def get_prefix(self, message: TwitchMessage) -> str: ...

    async def _dispatch(self, event: Event) -> None: ...

    async def _handle_command(self, event: Event) -> None: ...

    async def build_context(self, event: Event) -> Context: ...

    async def invoke_command(self, ctx: Context) -> None: ...

    async def can_run(self, ctx: Context) -> bool: ...

    async def on_privmsg(self, event: Event) -> None: ...

class TwitchMessage:

    __slots__ = ("id", "content", "bits", "emotes", "emote_only", "timestamp", "channel", "author")

    id: str
    content: str
    bits: int
    emotes: List[str]
    emote_only: bool
    timestamp: int

    channel: TwitchChannel
    author: TwitchUser

class Context(Messageable):

    __slots__ = ("bot", "message", "invoked_prefix", "args", "invoker", "command")

    bot: TwitchBot
    message: TwitchMessage
    invoked_prefix: str
    args: List[str]
    invoker: str
    command: Command

    @property
    def channel(self) -> TwitchChannel: ...

    @property
    def author(self) -> TwitchUser: ...

    @property
    def me(self) -> TwitchUser: ...

    @property
    def server(self) -> TwitchServer: ...

    async def send(self, message: str) -> None: ...

class Command:

    __slots__ = ("name", "callback", "active", "hidden", "aliases", "help", "params", "checks", "cooldowns")

    name: str
    callback: Coroutine
    active: bool
    hidden: bool
    aliases: List[str]
    help: str
    params: Dict[str, inspect.Parameter]
    checks: List[Union[Callable, Coroutine]]
    cooldowns: List[Cooldown]

    def __init__(self, name: str, callback: Coroutine, **options) -> None: ...

    def _parse_arguments(self, ctx: Context) -> Tuple[List[str], Dict[str]]: ...

    async def invoke(self, ctx: Context) -> None: ...

    async def can_run(self, ctx: Context) -> bool: ...

def command(name: str = ..., cls: type = ..., **attrs) -> Callable[[...], Command]: ...

def check(predicate: Union[Callable[[Context], bool], Coroutine[[Context], bool]]) -> Callable: ...

def broadcaster_only() -> Callable: ...

def mod_only() -> Callable: ...

def subscriber_only() -> Callable: ...

def cooldown(per: int, time: int, target: str = ...) -> Callable: ...