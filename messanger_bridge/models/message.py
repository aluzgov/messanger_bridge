import datetime
import enum

import pydantic


class MessangerEnum(enum.Enum):
    telegram = "telegram"
    discord = "discord"


class MessageFile(pydantic.BaseModel):
    name: str
    url: str


class Message(pydantic.BaseModel):
    message_id: str
    message: str
    chat_id: str
    user_id: str
    username: str
    timestamp: datetime.datetime
    messanger: MessangerEnum
    reply_to_id: str | None = None
    images: list[MessageFile] = pydantic.Field(default_factory=list)
    audios: list[MessageFile] = pydantic.Field(default_factory=list)
    videos: list[MessageFile] = pydantic.Field(default_factory=list)
    animations: list[MessageFile] = pydantic.Field(default_factory=list)
    documents: list[MessageFile] = pydantic.Field(default_factory=list)
    stickers: list[MessageFile] = pydantic.Field(default_factory=list)
