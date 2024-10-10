import datetime
import enum

import pydantic


class MessangerEnum(enum.Enum):
    telegram = "telegram"
    discord = "discord"


class Message(pydantic.BaseModel):
    message_id: str
    message: str
    chat_id: str
    user_id: str
    username: str
    timestamp: datetime.datetime
    messanger: MessangerEnum
    reply_to_id: str | None = None
