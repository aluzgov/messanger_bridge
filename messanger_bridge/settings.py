import pydantic
import pydantic_settings


class TransportSettings(pydantic_settings.BaseSettings):
    dsn: str
    queue: str


class MessangerSettings(pydantic_settings.BaseSettings):
    token: str
    dsn: str = ""
    admin_chats: list[str] = pydantic.Field(default_factory=list)
    moderation: bool = True


class StorageSettings(pydantic_settings.BaseSettings):
    dsn: str
    chat_id: str


class BridgeSettings(pydantic_settings.BaseSettings):
    name: str

    storage_dsn: str
    storage_chat_id: str

    transport_dsn: str
    transport_left_queue: str
    transport_right_queue: str

    messanger_left_token: str
    messanger_right_token: str
    messanger_left_dsn: str = ""
    messanger_right_dsn: str = ""
    messanger_left_admin_chats: list[str] = pydantic.Field(default_factory=list)
    messanger_right_admin_chats: list[str] = pydantic.Field(default_factory=list)
    messanger_left_moderation: bool = True
    messanger_right_moderation: bool = True

    @pydantic.field_validator("messanger_left_admin_chats", "messanger_right_admin_chats",
                              mode="before")
    def split_admin_chats(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',')]
        elif isinstance(v, int):
            return [str(v)]

        return v

    class Config:
        case_sensitive = False
        env_file_encoding = 'utf-8'
