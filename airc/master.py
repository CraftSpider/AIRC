"""
    Master class for the AIRC
"""

import asyncio

from .errors import HandlerError
from .enums import UserType
from .utils import insort, SortedHandler
from .server import TwitchServer


class ServerMaster:
    """
        The server handler acts similar to the normal reactor, holding a set of servers
        and passing events down to each one.
    """

    __slots__ = ("loop", "user_type", "connections", "handlers")

    def __init__(self, user_type=UserType.normal_user, loop=None):

        self.loop = loop or asyncio.get_event_loop()
        self.user_type = user_type

        self.connections = []
        self.handlers = {}

        self.add_global_handler("ping", _ponger)

    def server(self, user_type=None):
        user_type = user_type or self.user_type
        server = TwitchServer(self, user_type=user_type, loop=self.loop)
        self.connections.append(server)
        return server

    def add_global_handler(self, event, handler, priority=0):
        handler = SortedHandler(handler, priority)
        insort(self.handlers.setdefault(event, []), handler)

    def remove_global_handler(self, event, handler):
        handlers = self.handlers.get(event, [])
        for h in handlers:
            if h.handler == handler:
                handlers.remove(h)

    def run(self, *args, **kwargs):
        task = self.loop.create_task(self.start(*args, **kwargs))
        if not self.loop.is_running():
            self.loop.run_until_complete(task)

    async def start(self, *args, **kwargs):
        tasks = []
        uris = kwargs.get("uris", [])
        names = kwargs.get("names", [])
        passwds = kwargs.get("passwds", [])
        for server in self.connections:
            if not server.connected:
                await server.connect(uris.pop(0), names.pop(0), password=passwds.pop(0))
            tasks.append(self.loop.create_task(server.process_data()))
        while len(tasks) > 0:
            for task in tasks:
                task: asyncio.Task
                if task.done():
                    tasks.remove(task)
                    server = await task
                    tasks.append(self.loop.create_task(server.process_data()))
                elif task.cancelled():
                    tasks.remove(task)
            await asyncio.sleep(1)

    async def _handle_event(self, event):
        for handler in self.handlers.get("all_events", []):
            try:
                await handler(event)
            except Exception as e:
                raise HandlerError(e)
        for handler in self.handlers.get(event.type, []):
            try:
                await handler(event)
            except Exception as e:
                raise HandlerError(e)


async def _ponger(event):
    await event.server.pong(event.target)
