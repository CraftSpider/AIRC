"""
    Enums for the AIRC module
"""

import enum


class UserType(enum.Enum):

    normal_user = "USER"
    known_bot = "KNOWN"
    verified_bot = "VERIFIED"
