"""
    enum stubs for the AIRC module
"""

import enum


class UserType(enum.Enum):

    normal_user: str
    known_bot: str
    verified_bot: str