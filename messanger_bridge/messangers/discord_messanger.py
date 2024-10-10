import logging
from functools import partial
from io import BytesIO

import aiohttp
import discord

from messangers.abstract_messanger import AbstractMessanger
from models.message import Message, MessangerEnum, MessageFile

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
        audios = []
        videos = []
        animations = []
        documents = []
        for attachment in discord_message.attachments:
            if attachment.content_type.startswith("image"):
                message_file = MessageFile(name=attachment.filename, url=attachment.url)
                images.append(message_file)
            elif attachment.content_type.startswith("audio"):
                message_file = MessageFile(name=attachment.filename, url=attachment.url)
                audios.append(message_file)
            elif attachment.content_type.startswith("video"):
                message_file = MessageFile(name=attachment.filename, url=attachment.url)
                videos.append(message_file)
            elif attachment.filename.endswith(".gif"):
                message_file = MessageFile(name=attachment.filename, url=attachment.url)
                animations.append(message_file)
            else:
                message_file = MessageFile(name=attachment.filename, url=attachment.url)
                documents.append(message_file)

        message = Message(
            message_id=str(discord_message.id),
            message=discord_message.content,
            chat_id=str(discord_message.channel.id),
            user_id=str(discord_message.author.id),
            username=discord_message.author.display_name,
            timestamp=discord_message.created_at,
            messanger=MessangerEnum.discord,
            images=images,
            audios=audios,
            videos=videos,
            animations=animations,
            documents=documents,
        )
        await messanger.new_message(message=message)

    async def send_message(self, message: Message) -> None:
        username = (
            self.storage.get_nickname(author_id=message.chat_id) or message.username
        )
        recipients = self.storage.get_recipients(source_chat_id=message.chat_id)
        if not recipients:
            return None

        message_content = message.message
        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    self.settings.dsn,
                    session=session,
                )
                for image in message.images:
                    file_kwargs = {}
                    image_data = await download_file(session, image.url)
                    if image_data:
                        buffer = BytesIO(image_data)
                        file_kwargs["file"] = discord.File(buffer, filename=image.name)
                    else:
                        continue

                    await webhook.send(
                        message_content,
                        username=username,
                        **file_kwargs,
                    )
                    message_content = ""

                for audio in message.audios:
                    file_kwargs = {}
                    audio_data = await download_file(session, audio.url)
                    if audio_data:
                        buffer = BytesIO(audio_data)
                        file_kwargs["file"] = discord.File(buffer, filename=audio.name)
                    else:
                        continue

                    await webhook.send(
                        message_content,
                        username=username,
                        **file_kwargs,
                    )
                    message_content = ""

                for video in message.videos:
                    file_kwargs = {}
                    video_data = await download_file(session, video.url)
                    if video_data:
                        buffer = BytesIO(video_data)
                        file_kwargs["file"] = discord.File(buffer, filename=video.name)
                    else:
                        continue

                    await webhook.send(
                        message_content,
                        username=username,
                        **file_kwargs,
                    )
                    message_content = ""

                for animation in message.animations:
                    file_kwargs = {}
                    animation_data = await download_file(session, animation.url)
                    if animation_data:
                        buffer = BytesIO(animation_data)
                        file_kwargs["file"] = discord.File(buffer, filename=animation.name)
                    else:
                        continue

                    await webhook.send(
                        message_content,
                        username=username,
                        **file_kwargs,
                    )
                    message_content = ""

                for document in message.documents:
                    file_kwargs = {}
                    document_data = await download_file(session, document.url)
                    if document_data:
                        buffer = BytesIO(document_data)
                        file_kwargs["file"] = discord.File(buffer, filename=document.name)
                    else:
                        continue

                    await webhook.send(
                        message_content,
                        username=username,
                        **file_kwargs,
                    )
                    message_content = ""

                if message_content:
                    await webhook.send(
                        message_content,
                        username=username,
                    )
        except Exception:
            logger.exception("Error sending message")
