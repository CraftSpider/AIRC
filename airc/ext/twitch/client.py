"""
    Async IRC client.
    Supports the most of the IRC protocol, and also the specialization used by twitch.

    author: CraftSpider
"""

import logging
import asyncio
import abc

from airc.errors import HandlerError
from airc.enums import UserType
from airc.client import DefaultClient

log = logging.getLogger("airc.twitch_client")


async def empty_handler(event): pass


def empty_handler_sync(event): pass


class TwitchClient(DefaultClient):
    # This thing needs to have event handlers for users joining, leaving, channel joins, etc.
    # Keep track of what caps we have, and more.

    __slots__ = ("master", "server", "membership", "commands", "tags", "channels")

    def __init__(self, user_type=UserType.normal_user, loop=None):
        loop = loop or asyncio.get_event_loop()
        self.master = None
        self.server = self.master.server()
        self.master.add_global_handler("all_events", self._dispatch)

        self.membership = False
        self.commands = False
        self.tags = False

        self.channels = []  # list of channels we're in

    def run(self, uri, username, password):
        kwargs = {"uris": [uri], "names": [username], "passwds": [password]}
        self.master.run(**kwargs)

    def get_channel(self, name):
        for channel in self.channels:
            if channel.name == name:
                return channel
        return None

    def create_channel(self, name):
        channel = TwitchChannel(name, self.server)
        self.channels.append(channel)
        return channel

    async def _dispatch(self, event):
        handler = getattr(self, "handle_" + event.type, empty_handler_sync)
        try:
            handler(event)
        except Exception as e:
            raise HandlerError(e)
        handler = getattr(self, "on_" + event.type, empty_handler)
        try:
            await handler(event)
        except Exception as e:
            raise HandlerError(e)

    def handle_cap(self, event):
        if event.arguments[0] == "ACK":
            if event.arguments[1].endswith("commands"):
                self.commands = True
            elif event.arguments[1].endswith("membership"):
                self.membership = True
            elif event.arguments[1].endswith("tags"):
                self.tags = True

    def handle_join(self, event):
        channel = self.get_channel(event.target)
        if channel is None:
            channel = self.create_channel(event.target)
        channel.create_user(event.prefix.nick)

    def handle_mode(self, event):
        mode, name = event.arguments
        channel = self.get_channel(event.target)
        for user in channel.users:
            if user.name == name:
                user.set_mode(mode)

    def handle_namreply(self, event):
        channel = self.get_channel(event.arguments[1])
        if channel is None:
            channel = self.create_channel(event.arguments[1])
        for name in event.arguments[2:]:
            channel.create_user(name)

    def handle_part(self, event):
        channel = self.get_channel(event.target)
        user = event.prefix.nick
        channel.remove_user(user)
        if user == self.server.username and channel:
            self.channels.remove(channel)

    def handle_privmsg(self, event):
        channel = self.get_channel(event.target)
        user = channel.get_user(event.prefix.nick)
        if user is None:
            user = channel.create_user(event.prefix.nick)
        user.set_state(event.tags)

    def handle_roomstate(self, event):
        channel = self.get_channel(event.target)
        if channel is None:
            channel = self.create_channel(event.target)
        channel.set_state(event.tags)

    def handle_userstate(self, event):
        channel = self.get_channel(event.target)
        user = channel.get_user(self.server.username)
        if not user:
            channel.create_user(self.server.username)
        user.set_state(event.tags)


class Messageable(abc.ABC):

    __slots__ = ()

    @abc.abstractmethod
    async def send(self, message):
        raise NotImplementedError


class TwitchChannel(Messageable):

    __slots__ = ("id", "name", "lang", "emote_only", "follower_only", "mercury", "r9k", "rituals", "slow", "sub_only",
                 "users", "server")

    def __init__(self, name, server):
        self.id = -1
        self.name = name
        self.lang = None
        self.emote_only = False
        self.follower_only = False
        self.mercury = False
        self.r9k = False
        self.rituals = False
        self.slow = 0
        self.sub_only = False

        self.server = server
        self.users = []

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, TwitchChannel):
            return self.name == other.name
        return False

    def __str__(self):
        return f"TwitchChannel(name: '{self.name}', id: '{self.id}')"

    @property
    def me(self):
        return self.get_user(self.server.username)

    def set_state(self, tags):
        self.lang = tags.get("broadcaster-lang", self.lang)
        self.emote_only = bool(int(tags.get("emote-only", self.emote_only)))
        self.follower_only = bool(int(tags.get("followers-only", int(self.follower_only) - 1)) + 1)
        self.mercury = bool(int(tags.get("mercury", self.mercury)))
        self.r9k = bool(int(tags.get("r9k", self.r9k)))
        self.rituals = bool(int(tags.get("rituals", self.rituals)))
        self.id = int(tags.get("room-id", self.id))
        self.slow = int(tags.get("slow", self.slow))
        self.sub_only = bool(int(tags.get("subs-only", self.sub_only)))

    def create_user(self, name):
        for user in self.users:
            if user.name == name:
                break
        else:
            user = TwitchUser(name, self, self.server)
            self.users.append(user)
        return user

    def get_user(self, name):
        for user in self.users:
            if user.name == name:
                return user
        return None

    def remove_user(self, name):
        user = self.get_user(name)
        if user:
            self.users.remove(user)

    async def send(self, message):
        message = str(message)
        await self.server.privmsg(self.name, message)


def _process_badges(badge_str):
    if badge_str is None:
        return {}
    badges = badge_str.split(",")
    badges = dict((k, int(v)) for k, v in map(lambda x: x.split("/"), badges))
    return badges


class TwitchUser(Messageable):

    __slots__ = ("id", "name", "display_name", "turbo", "partner", "mod", "global_mod", "admin", "staff", "broadcaster",
                 "subscriber", "color", "badges", "sub_length", "bit_level", "server", "channel")

    def __init__(self, name, channel, server):
        self.server = server
        self.channel = channel
        self.id = -1
        self.name = name
        self.display_name = name

        self.turbo = False
        self.partner = False
        self.mod = False
        self.global_mod = False
        self.admin = False
        self.staff = False
        self.broadcaster = False
        self.subscriber = False

        self.badges = {}
        self.sub_length = -1
        self.bit_level = -1
        self.color = None

    def __str__(self):
        return f"TwitchUser(name: '{self.name}', id: '{self.id}')"

    def set_state(self, tags):
        self.badges = _process_badges(tags.get("badges", ""))
        for badge in self.badges:
            if badge == "broadcaster":
                self.broadcaster = True
            elif badge == "partner":
                self.partner = True
            elif badge == "subscriber":
                self.sub_length = self.badges[badge]
            elif badge == "bits":
                self.bit_level = self.badges[badge]

        self.color = tags.get("color", self.color)
        self.display_name = tags.get("display-name", self.display_name)
        self.mod = bool(int(tags.get("mod", self.mod)))
        self.subscriber = bool(int(tags.get("subscriber", self.subscriber)))
        self.turbo = bool(int(tags.get("turbo", self.turbo)))
        self.id = int(tags.get("user-id", self.id))

        user_type = tags.get("user-type", None)
        if user_type:
            if user_type == "mod":
                self.mod = True
            elif user_type == "global_mod":
                self.global_mod = True
            elif user_type == "admin":
                self.admin = True
            elif user_type == "staff":
                self.staff = True

    def set_mode(self, mode):
        if mode[0] == "-":
            self.mod = False
        elif mode[0] == "+":
            self.mod = True

    async def send(self, message):
        message = str(message)
        self.server.privmsg("#jtv", f"/w {self.name} {message}")

    async def timeout(self, length):
        self.server.privmsg(self.channel.name, f"/timeout {self.name} {length}")

    async def ban(self):
        self.server.privmsg(self.channel.name, f"/ban {self.name}")

    async def unban(self):
        self.server.privmsg(self.channel.name, f"/unban {self.name}")
