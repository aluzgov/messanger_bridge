import abc
import typing

from models.message import Message
from settings import TransportSettings


class AbstractTransport(abc.ABC):

    def __init__(self, settings: TransportSettings) -> None:
        self.settings = settings

    @abc.abstractmethod
    async def send(self, message: Message) -> None:
        pass

    @abc.abstractmethod
    def messages(self) -> typing.Generator[Message, None, None]:
        pass
