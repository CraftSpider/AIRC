
import asyncio
import websockets

from airc.server import DefaultServer
from airc.enums import UserType
from airc.utils import LineBuffer, Cooldown


class TwitchServer(DefaultServer):
    """
        The TwitchServer represents a single connection to Twitch. It holds methods to support
        any possible message that Twitch understands.
    """

    __slots__ = ("user_type", "cooldown", "buffer", "uri", "username", "password")

    mod_cooldown = Cooldown(100, 30)
    join_cooldown = Cooldown(50, 15)

    def __init__(self, master=None, user_type=UserType.normal_user, loop=None):
        super().__init__(master, loop=loop)
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

    async def reconnect(self):
        self.socket = await websockets.connect(self.uri, ssl=None)
        self.connected = True

        await self.pass_(self.password)
        await self.nick(self.username)
        await self.user(self.username, self.username)

    async def req_commands(self):
        await self.cap("REQ", "twitch.tv/commands")

    async def req_membership(self):
        await self.cap("REQ", "twitch.tv/membership")

    async def req_tags(self):
        await self.cap("REQ", "twitch.tv/tags")

    async def send_raw(self, data):
        if data.startswith("JOIN "):
            wait = self.join_cooldown.can_run()
            while wait:
                await asyncio.sleep(wait)
                wait = self.join_cooldown.can_run()
        else:
            wait = self.cooldown.can_run()
            while wait:
                await asyncio.sleep(wait)
                wait = self.cooldown.can_run()
        await self.socket.send(data)