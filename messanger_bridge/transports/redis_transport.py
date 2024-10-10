import contextlib
import typing

import pottery
from pottery import QueueEmptyError
from redis.client import Redis

from models.message import Message
from settings import TransportSettings
from transports.abstract_transport import AbstractTransport


class RedisTransport(AbstractTransport):

    def __init__(self, settings: TransportSettings) -> None:
        super().__init__(settings)
        self.redis = Redis.from_url(self.settings.dsn)
        self.queue = pottery.RedisSimpleQueue(redis=self.redis, key=self.settings.queue)

    async def send(self, message: Message) -> None:
        self.queue.put(message.model_dump_json())

    def messages(self) -> typing.AsyncGenerator[Message, None]:
        while True:
            with contextlib.suppress(Exception):
                item = self.queue.get()
                message = Message.model_validate_json(item)
                yield message
