
import airc
import asyncio
import logging


log = logging.getLogger()
log.setLevel(logging.INFO)
loop = asyncio.get_event_loop()


# class Talos(airc.TwitchBot):
#
#     async def on_welcome(self, event):
#         await self.server.req_commands()
#         await self.server.req_membership()
#         await self.server.req_tags()
#         await self.server.join("#craftspider")
#
#
# uri = "ws://irc-ws.chat.twitch.tv"
# passw = "oauth:{}"
#
# talos = Talos("^")
#
#
# @talos.command()
# async def test(ctx):
#     print(ctx.me)
#
#
# @talos.command()
# async def help(ctx, command):
#     await ctx.send(command)
#
# talos.run(uri=uri, username="talos_bot_", password=passw)

class TestClient(airc.DefaultClient):

    async def on_all_events(self, event):
        print(event)


client = TestClient("ws://localhost:6667")
client.run(names=["talos"], passwds=[""])
