import contextlib
import pathlib

import pydantic

from settings import StorageSettings
from storages.abstract_storage import AbstractStorage, UserModel


class DataModel(pydantic.BaseModel):
    recipients_map: dict[str, set[str]] = {}
    nickname_map: dict[str, str] = {}
    banned_users: set[str] = set()
    on_moderation: set[str] = set()
    moderated_users: set[str] = set()


class StaticStorage(AbstractStorage):

    def __init__(self, settings: StorageSettings) -> None:
        super().__init__(settings)
        filepath = pathlib.Path(settings.dsn)
        if filepath.exists():
            with filepath.open() as f:
                self.data = DataModel.model_validate_json(f.read())
        else:
            self.data = DataModel()

    def get_recipients(self, source_chat_id: str) -> list[str]:
        return [item for item in self.data.recipients_map.get(source_chat_id, [])]

    def set_nickname(self, author_id: str, nickname: str) -> None:
        self.data.nickname_map[author_id] = nickname
        self.dump()

    def is_banned(self, chat_id: str) -> bool:
        return chat_id in self.data.banned_users

    def connect(self, source_chat_id: str) -> None:
        if source_chat_id not in self.data.recipients_map:
            self.data.recipients_map[source_chat_id] = set()

        self.data.recipients_map[source_chat_id].add(self.settings.chat_id)

        if self.settings.chat_id not in self.data.recipients_map:
            self.data.recipients_map[self.settings.chat_id] = set()

        self.data.recipients_map[self.settings.chat_id].add(source_chat_id)
        self.dump()

    def disconnect(self, source_chat_id: str) -> None:
        if source_chat_id in self.data.recipients_map:
            with contextlib.suppress(KeyError):
                self.data.recipients_map[source_chat_id].remove(self.settings.chat_id)

        if self.settings.chat_id in self.data.recipients_map:
            with contextlib.suppress(KeyError):
                self.data.recipients_map[self.settings.chat_id].remove(source_chat_id)

        self.dump()

    def get_nickname(self, author_id: str) -> str | None:
        return self.data.nickname_map.get(author_id, None)

    def dump(self) -> None:
        with pathlib.Path(self.settings.dsn).open("w") as f:
            f.write(self.data.model_dump_json())

    def ban(self, chat_id: str) -> None:
        self.data.banned_users.add(chat_id)
        self.disconnect(chat_id)
        self.dump()

    def unban(self, chat_id: str) -> None:
        with contextlib.suppress(KeyError):
            self.data.banned_users.remove(chat_id)
        self.dump()

    def list_of_users(self) -> list[UserModel]:
        connected_users = self.data.recipients_map.get(self.settings.chat_id, set())
        return [
            UserModel(
                chat_id=chat_id, nickname=self.data.nickname_map.get(chat_id, "no nick")
            )
            for chat_id in connected_users
        ]

    def list_of_moderation(self) -> list[UserModel]:
        return [
            UserModel(
                chat_id=chat_id, nickname=self.data.nickname_map.get(chat_id, "no nick")
            )
            for chat_id in self.data.on_moderation
        ]

    def list_of_nicknames(self) -> list[UserModel]:
        return [
            UserModel(chat_id=chat_id, nickname=nickname)
            for chat_id, nickname in self.data.nickname_map.items()
        ]

    def approve(self, chat_id: str) -> None:
        with contextlib.suppress(KeyError):
            self.data.on_moderation.remove(chat_id)

        self.data.moderated_users.add(chat_id)

        self.connect(chat_id)
        self.dump()

    def moderate(self, chat_id: str) -> None:
        self.data.on_moderation.add(chat_id)
        self.dump()

    def is_moderated(self, chat_id: str) -> bool:
        return chat_id in self.data.moderated_users
