
import enum


class TwitchReplyType(enum.Enum):
    pass


twitch = [
    "whisper",
    "clearchat",
    "globaluserstate",
    "roomstate",
    "usernotice",
    "userstate",
    "hosttarget",
    "notice",
    "reconnect"
]


class UserType(enum.Enum):

    normal_user = "USER"
    known_bot = "KNOWN"
    verified_bot = "VERIFIED"
