
import asyncio
import airc


class SimpleClient(airc.DefaultClient):

    async def on_privmsg(self, event):
        print(f"<{event.prefix.nick}> {event.arguments[0]}")

    async def run(self):
        self.loop.create_task(self.start(names=["craftspider"], passwds=[""]))
        conn = self.connections[0]

        while not conn.socket:
            await asyncio.sleep(.1)

        await conn.join("#test")
        while True:
            value = await self.loop.run_in_executor(None, input, "> ")
            if value.startswith("/"):
                vals = value.split(" ")
                vals[0] = vals[0][1:]
                await conn.send_items(*vals)
            await conn.privmsg("#test", value)


client = SimpleClient("ws://localhost:6667")
task = asyncio.get_event_loop().create_task(client.run())
asyncio.get_event_loop().run_until_complete(task)
