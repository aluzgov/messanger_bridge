import logging
from functools import partial
from io import BytesIO

import aiohttp
import discord

from messangers.abstract_messanger import AbstractMessanger
from models.message import Message, MessangerEnum

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    pass


async def download_file(session: aiohttp.ClientSession, url: str) -> bytes | None:
    chunks = []
    max_file_size = 8 * 1024 * 1024
    async with session.get(url) as response:
        downloaded_size = 0
        async for chunk in response.content.iter_chunked(1024):
            downloaded_size += len(chunk)
            if downloaded_size > max_file_size:
                logger.warning("File %s too large", url)
                return None

            chunks.append(chunk)
        file_bytes = b''.join(chunks)
        return file_bytes


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

        images = []
        for attachment in discord_message.attachments:
            if attachment.content_type.startswith("image"):
                images.append(attachment.url)

        message = Message(
            message_id=str(discord_message.id),
            message=discord_message.content,
            chat_id=str(discord_message.channel.id),
            user_id=str(discord_message.author.id),
            username=discord_message.author.display_name,
            timestamp=discord_message.created_at,
            messanger=MessangerEnum.discord,
            images=images,
        )
        await messanger.new_message(message=message)

    async def send_message(self, message: Message) -> None:
        username = (
            self.storage.get_nickname(author_id=message.chat_id) or message.username
        )
        recipients = self.storage.get_recipients(source_chat_id=message.chat_id)
        if not recipients:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                file_kwargs = {}
                if message.images:
                    image_data = await download_file(session, message.images[0])
                    if image_data:
                        buffer = BytesIO(image_data)
                        file_kwargs["file"] = discord.File(buffer, filename="image.png")

                webhook = discord.Webhook.from_url(
                    self.settings.dsn,
                    session=session,
                )
                await webhook.send(
                    message.message,
                    username=username,
                    **file_kwargs,
                )
        except Exception:
            logger.exception("Error sending message")
