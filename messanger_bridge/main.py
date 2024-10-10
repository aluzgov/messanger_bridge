import logging
import multiprocessing
import os
import pathlib

from bridges.simple_bridge import SimpleBridge
from messangers.discord_messanger import DiscordMessanger
from messangers.telegram_messanger import TelegramMessanger
from settings import (
    StorageSettings,
    TransportSettings,
    MessangerSettings,
    BridgeSettings,
)
from storages.static_storage import StaticStorage
from transports.redis_transport import RedisTransport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def run_bridge(file_name: pathlib.Path, bridge_name: str, base_dir: pathlib.Path):
    storage_dsn = pathlib.Path(
        base_dir, "data", f"{bridge_name}.json"
    )
    bridge_settings = BridgeSettings(
        name=bridge_name,
        storage_dsn=str(storage_dsn),
        transport_left_queue=f"{bridge_name}_queue_left",
        transport_right_queue=f"{bridge_name}_queue_right",
        _env_file=str(file_name),
    )

    storage_settings = StorageSettings(
        dsn=bridge_settings.storage_dsn,
        chat_id=bridge_settings.storage_chat_id,
    )
    storage = StaticStorage(settings=storage_settings)
    discord_transport = RedisTransport(
        settings=TransportSettings(
            dsn=bridge_settings.transport_dsn,
            queue=bridge_settings.transport_left_queue,
        )
    )
    telegram_transport = RedisTransport(
        settings=TransportSettings(
            dsn=bridge_settings.transport_dsn,
            queue=bridge_settings.transport_right_queue,
        )
    )
    discord_settings = MessangerSettings(
        token=bridge_settings.messanger_right_token,
        dsn=bridge_settings.messanger_right_dsn,
        admin_chats=bridge_settings.messanger_right_admin_chats,
        moderation=bridge_settings.messanger_right_moderation,
    )
    discord_messanger = DiscordMessanger(
        settings=discord_settings, transport=discord_transport, storage=storage
    )
    telegram_settings = MessangerSettings(
        token=bridge_settings.messanger_left_token,
        dsn=bridge_settings.messanger_left_dsn,
        admin_chats=bridge_settings.messanger_left_admin_chats,
        moderation=bridge_settings.messanger_left_moderation,
    )
    telegram_messanger = TelegramMessanger(
        settings=telegram_settings, transport=telegram_transport, storage=storage
    )
    bridge = SimpleBridge(left=telegram_messanger, right=discord_messanger)
    bridge.run()


def main():
    logging.info("Starting...")
    multiprocessing.set_start_method('spawn')

    base_dir = pathlib.Path(__file__).resolve().parent.parent
    config_path = pathlib.Path(base_dir, "messangers")
    processes = []

    for file_name in config_path.glob(".*.env"):
        bridge_name = file_name.name[1:-4]
        p = multiprocessing.Process(target=run_bridge, args=(file_name, bridge_name, base_dir),
                                    name=bridge_name)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
