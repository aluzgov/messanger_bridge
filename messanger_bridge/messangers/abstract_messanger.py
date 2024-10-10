import abc

from models.message import Message
from settings import MessangerSettings
from storages.abstract_storage import AbstractStorage
from transports.abstract_transport import AbstractTransport


class AbstractMessanger(abc.ABC):

    def __init__(
        self,
        settings: MessangerSettings,
        transport: AbstractTransport,
        storage: AbstractStorage,
    ) -> None:
        self.settings = settings
        self.transport = transport
        self.storage = storage

    @abc.abstractmethod
    def run(self) -> None:
        pass

    @abc.abstractmethod
    async def send_message(self, message: Message) -> None:
        pass

    async def new_message(self, message: Message) -> None:
        await self.transport.send(message=message)
