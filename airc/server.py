"""
    Server classes for the AIRC
"""


import re
import abc
import asyncio
import logging
import websockets

from .enums import UserType
from .errors import *
from .events import numeric, Event
from .utils import insort, LineBuffer, Cooldown, SortedHandler, IRCPrefix


log = logging.getLogger("airc.server")
_cap_subcommands = set('LS LIST REQ ACK NAK CLEAR END'.split())
_client_subcommands = set(_cap_subcommands) - {'NAK'}
_rfc_pattern = r"^(@(?P<tags>[^ ]*) )?(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?"
_regexp_rfc = re.compile(_rfc_pattern)


def _handle_tags(tags):
    if tags is None:
        return {}
    tags = tags.lstrip("@")
    raw_tags = tags.split(";")
    tags = {}
    for raw_tag in raw_tags:
        name, val = raw_tag.split("=")
        if val == "":
            val = None
        tags[name] = val
    return tags


def _handle_args(args):
    args = args.lstrip()
    out_args = []
    rest = False
    tmp = ""
    for char in args:
        if rest:
            tmp += char
        elif char == " ":
            out_args.append(tmp)
            tmp = ""
        elif char == ":" and tmp == "":
            rest = True
        else:
            tmp += char
    if tmp:
        out_args.append(tmp)
    return out_args


def _handle_command(command):
    return numeric.get(command, command.lower())


def _handle_prefix(prefix):
    return IRCPrefix(prefix)


class Server:
    """
        Generic IRC connection. Subclassed by specific kinds of servers.
    """

    __slots__ = ("loop", "master", "handlers", "socket", "connected")

    def __init__(self, master=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.master = master

        self.handlers = {}
        self.socket = None
        self.connected = False

    def add_global_handler(self, event, handler, priority=0):
        if self.master:
            self.master.add_global_handler(event, handler, priority)

    def remove_global_handler(self, event, handler):
        if self.master:
            self.master.remove_global_handler(event, handler)

    def add_handler(self, event, handler, priority=0):
        handler = SortedHandler(handler, priority)
        li = self.handlers.setdefault(event, [])
        insort(li, handler)

    def remove_handler(self, event, handler):
        handlers = self.handlers.get(event, [])
        for h in handlers:
            if h.handler == handler:
                handlers.remove(h)

    @abc.abstractmethod
    async def connect(self, uri, name, password=""):
        raise NotImplementedError

    @abc.abstractmethod
    async def process_data(self):
        raise NotImplementedError


class TwitchServer(Server):
    """
        The TwitchServer represents a single connection to Twitch. It holds methods to support
        any possible message that Twitch understands.
    """

    __slots__ = ("user_type", "cooldown", "buffer", "uri", "username", "password")

    mod_cooldown = Cooldown(100, 30)
    join_cooldown = Cooldown(50, 15)

    def __init__(self, master=None, user_type=UserType.normal_user, loop=None):
        super().__init__(master, loop)
        self.user_type = user_type
        if user_type == UserType.normal_user:
            self.cooldown = Cooldown(20, 30)
        elif user_type == UserType.known_bot:
            self.cooldown = Cooldown(50, 30)
        elif user_type == UserType.verified_bot:
            self.cooldown = Cooldown(7500, 30)
        else:
            self.cooldown = Cooldown(20, 30)

        self.buffer = LineBuffer()
        self.uri = None
        self.username = None
        self.password = None

    def __str__(self):
        return f"TwitchServer(uri" \
               f": '{self.uri}', name: '{self.username}')"

    async def connect(self, uri, username, password=""):
        self.uri = uri
        self.socket = await websockets.connect(self.uri, ssl=None)
        self.username = username
        self.password = password
        self.connected = True

        await self.pass_(self.password)
        await self.nick(self.username)
        await self.user(self.username, self.username)

    async def disconnect(self):
        self.socket = None
        self.connected = False

    async def reconnect(self):
        self.socket = await websockets.connect(self.uri, ssl=None)
        self.connected = True

        await self.pass_(self.password)
        await self.nick(self.username)
        await self.user(self.username, self.username)

    async def process_data(self):
        try:
            data = await self.socket.recv()
        except websockets.ConnectionClosed:
            await self.disconnect()
            raise
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        if chr(data[-1]) != "\n":
            data += b'\n'

        self.buffer.feed(data)

        for line in self.buffer:
            if not line:
                continue
            await self._process_line(line)

        return self

    async def _process_line(self, line):
        # Dispatch an all_raw_events event
        event = Event(self, "all_raw_events", [line])
        await self._handle_event(event)

        match = _regexp_rfc.match(line)
        command = _handle_command(match.group('command'))
        args = _handle_args(match.group('argument'))
        tags = _handle_tags(match.group('tags'))
        prefix = _handle_prefix(match.group('prefix'))

        # Dispatch the actual specific event
        event = Event(self, command, args, prefix, tags)
        log.info(event)
        await self._handle_event(event)

    async def _handle_event(self, event):
        if self.master:
            self.loop.create_task(self.master._handle_event(event))
        for handler in self.handlers.get("all_events", ()):
            try:
                await handler(event)
            except Exception as e:
                raise HandlerError(e)
        for handler in self.handlers.get(event.type, ()):
            try:
                await handler(event)
            except Exception as e:
                raise HandlerError(e)

    async def cap(self, sub, *args):
        if sub not in _client_subcommands:
            raise AIRCError
        if len(args) > 1:
            args = (":" + args[0],) + args[1:]
        await self.send_items("CAP", sub, *args)

    async def join(self, channel):
        await self.send_items("JOIN", channel)

    async def nick(self, newnick):
        await self.send_items("NICK", newnick)

    async def part(self, channel):
        await self.send_items("PART", channel)

    async def pass_(self, password):
        await self.send_items("PASS", password)

    async def pong(self, loc):
        await self.send_items("PONG", loc)

    async def privmsg(self, channel, message):
        await self.send_items("PRIVMSG", channel, ":" + message)

    async def quit(self, message):
        await self.send_items("QUIT", ":" + message)
        await self.disconnect()

    async def req_commands(self):
        await self.cap("REQ", "twitch.tv/commands")

    async def req_membership(self):
        await self.cap("REQ", "twitch.tv/membership")

    async def req_tags(self):
        await self.cap("REQ", "twitch.tv/tags")

    async def user(self, username, realname):
        cmd = f"USER {username} 0 * : {realname}"
        await self.send_raw(cmd)

    async def send_items(self, *items):
        await self.send_raw(' '.join(filter(None, items)))

    async def send_raw(self, raw):
        if raw.startswith("JOIN "):
            wait = self.join_cooldown.can_run()
            while wait:
                await asyncio.sleep(wait)
                wait = self.join_cooldown.can_run()
        else:
            wait = self.cooldown.can_run()
            while wait:
                await asyncio.sleep(wait)
                wait = self.cooldown.can_run()
        await self.socket.send(raw)
