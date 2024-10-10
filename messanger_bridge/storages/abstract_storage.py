import abc

import pydantic

from settings import StorageSettings


class UserModel(pydantic.BaseModel):
    chat_id: str
    nickname: str


class AbstractStorage(abc.ABC):

    def __init__(self, settings: StorageSettings) -> None:
        self.settings = settings

    @abc.abstractmethod
    def get_recipients(self, source_chat_id: str) -> list[str]:
        pass

    @abc.abstractmethod
    def get_nickname(self, author_id: str) -> str | None:
        pass

    @abc.abstractmethod
    def set_nickname(self, author_id: str, nickname: str) -> None:
        pass

    @abc.abstractmethod
    def connect(self, source_chat_id: str) -> None:
        pass

    @abc.abstractmethod
    def disconnect(self, source_chat_id: str) -> None:
        pass

    @abc.abstractmethod
    def is_banned(self, chat_id: str) -> bool:
        pass

    @abc.abstractmethod
    def ban(self, chat_id: str) -> None:
        pass

    @abc.abstractmethod
    def unban(self, chat_id: str) -> None:
        pass

    @abc.abstractmethod
    def list_of_users(self) -> list[UserModel]:
        return []

    @abc.abstractmethod
    def list_of_moderation(self) -> list[UserModel]:
        return []

    @abc.abstractmethod
    def approve(self, chat_id: str) -> None:
        pass

    @abc.abstractmethod
    def moderate(self, chat_id: str) -> None:
        pass
