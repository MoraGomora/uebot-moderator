from enum import Enum

class CommandAccessLevel(Enum):
    USER = "user"
    PUBLIC = "public"
    PRIVATE = "private"

class ModerationMode(Enum):
    TOXICITY = "toxicity"
    ADS = "ads"