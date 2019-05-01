


class TwitchMessage:

    __slots__ = ("id", "content", "bits", "emotes", "emote_only", "timestamp", "channel", "author")

    def __init__(self, event, channel, author):
        tags = event.tags
        self.id = tags.get("id", "")
        self.content = event.arguments[0]
        self.bits = int(tags.get("bits", 0))
        self.emotes = tags.get("emotes")
        self.emote_only = bool(int(tags.get("emote-only", False)))
        self.timestamp = int(tags.get("tmi-sent-ts", -1))

        self.channel = channel
        self.author = author
