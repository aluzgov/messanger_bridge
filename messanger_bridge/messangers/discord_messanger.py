import logging
from functools import partial

import aiohttp
import discord

from messangers.abstract_messanger import AbstractMessanger
from models.message import Message, MessangerEnum

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    pass


class DiscordMessanger(AbstractMessanger):

    def run(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        client = DiscordClient(intents=intents)
        client.on_message = partial(
            staticmethod(self.on_message), messanger=self, client=client
        )
        client.run(self.settings.token)

    @staticmethod
    async def on_message(
        discord_message: discord.Message,
        *,
        client: DiscordClient,
        messanger: "DiscordMessanger",
    ) -> None:
        myself = discord_message.author == client.user
        if myself:
            return None

        message = Message(
            message_id=str(discord_message.id),
            message=discord_message.content,
            chat_id=str(discord_message.channel.id),
            user_id=str(discord_message.author.id),
            username=discord_message.author.display_name,
            timestamp=discord_message.created_at,
            messanger=MessangerEnum.discord,
        )
        await messanger.new_message(message=message)

    async def send_message(self, message: Message) -> None:
        username = (
            self.storage.get_nickname(author_id=message.chat_id) or message.username
        )
        recipients = self.storage.get_recipients(source_chat_id=message.chat_id)
        if not recipients:
            return None

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                self.settings.dsn,
                session=session,
            )
            await webhook.send(
                message.message,
                username=username,
            )
