import asyncio
import logging
import typing

from telegram import Update, Bot, InputMediaPhoto, InputMediaAudio, InputMediaVideo, \
    InputMediaDocument
from telegram.error import Forbidden
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)

from messangers.abstract_messanger import AbstractMessanger
from models.message import Message, MessangerEnum, MessageFile

logger = logging.getLogger(__name__)


class TelegramMessanger(AbstractMessanger):

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def process_messages():
            application = Application.builder().token(self.settings.token).build()

            application.add_handler(
                MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_text_message)
            )
            application.add_handler(
                MessageHandler(filters.PHOTO & (~filters.COMMAND), self.handle_photo)
            )
            application.add_handler(
                MessageHandler(filters.AUDIO & (~filters.COMMAND), self.handle_audio)
            )
            application.add_handler(
                MessageHandler(filters.VIDEO & (~filters.COMMAND), self.handle_video)
            )
            application.add_handler(
                MessageHandler(filters.ANIMATION & (~filters.COMMAND), self.handle_animation)
            )
            application.add_handler(
                MessageHandler(filters.ATTACHMENT & (~filters.COMMAND), self.handle_attachment)
            )
            application.add_handler(
                CommandHandler(["start", "help"], self.handle_start)
            )
            application.add_handler(CommandHandler("connect", self.handle_connect))
            application.add_handler(
                CommandHandler("disconnect", self.handle_disconnect)
            )
            application.add_handler(
                CommandHandler("nickname", self.handle_set_nickname)
            )
            application.add_handler(CommandHandler("ban", self.handle_ban))
            application.add_handler(CommandHandler("unban", self.handle_unban))
            application.add_handler(CommandHandler("users", self.handle_list_of_users))
            application.add_handler(CommandHandler("approve", self.handle_approve))
            application.add_handler(CommandHandler("on_moderation", self.handle_on_moderation))

            await application.initialize()
            await application.start()
            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            await asyncio.Event().wait()

        try:
            loop.run_until_complete(process_messages())
        finally:
            loop.close()

    async def handle_text_message(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = (
                update.message.from_user.username or update.message.from_user.first_name
        )
        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = str(update.message.reply_to_message.message_id)

        message = Message(
            message_id=str(update.message.message_id),
            message=update.message.text,
            chat_id=str(update.message.chat_id),
            user_id=str(update.message.from_user.id),
            username=username,
            timestamp=update.message.date,
            messanger=MessangerEnum.telegram,
            reply_to_id=reply_to_id,
        )
        await self.new_message(message=message)

    async def handle_photo(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = (
                update.message.from_user.username or update.message.from_user.first_name
        )
        images = []
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path
            message_file = MessageFile(name="image.png", url=file_path)
            images.append(message_file)

        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = str(update.message.reply_to_message.message_id)

        message = Message(
            message_id=str(update.message.message_id),
            message=update.message.caption or "",
            chat_id=str(update.message.chat_id),
            user_id=str(update.message.from_user.id),
            username=username,
            timestamp=update.message.date,
            messanger=MessangerEnum.telegram,
            reply_to_id=reply_to_id,
            images=images,
        )
        await self.new_message(message=message)

    async def handle_audio(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = (
                update.message.from_user.username or update.message.from_user.first_name
        )
        audios = []
        if update.message.audio:
            file_id = update.message.audio.file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path
            message_file = MessageFile(name=update.message.audio.file_name, url=file_path)
            audios.append(message_file)

        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = str(update.message.reply_to_message.message_id)

        message = Message(
            message_id=str(update.message.message_id),
            message=update.message.caption or "",
            chat_id=str(update.message.chat_id),
            user_id=str(update.message.from_user.id),
            username=username,
            timestamp=update.message.date,
            messanger=MessangerEnum.telegram,
            reply_to_id=reply_to_id,
            audios=audios,
        )
        await self.new_message(message=message)

    async def handle_video(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = (
                update.message.from_user.username or update.message.from_user.first_name
        )
        videos = []
        if update.message.video:
            file_id = update.message.video.file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path
            message_file = MessageFile(name=update.message.video.file_name, url=file_path)
            videos.append(message_file)

        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = str(update.message.reply_to_message.message_id)

        message = Message(
            message_id=str(update.message.message_id),
            message=update.message.caption or "",
            chat_id=str(update.message.chat_id),
            user_id=str(update.message.from_user.id),
            username=username,
            timestamp=update.message.date,
            messanger=MessangerEnum.telegram,
            reply_to_id=reply_to_id,
            videos=videos,
        )
        await self.new_message(message=message)

    async def handle_animation(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = (
                update.message.from_user.username or update.message.from_user.first_name
        )
        animations = []
        if update.message.animation:
            file_id = update.message.animation.file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path
            message_file = MessageFile(name=update.message.animation.file_name, url=file_path)
            animations.append(message_file)

        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = str(update.message.reply_to_message.message_id)

        message = Message(
            message_id=str(update.message.message_id),
            message=update.message.caption or "",
            chat_id=str(update.message.chat_id),
            user_id=str(update.message.from_user.id),
            username=username,
            timestamp=update.message.date,
            messanger=MessangerEnum.telegram,
            reply_to_id=reply_to_id,
            animations=animations,
        )
        await self.new_message(message=message)

    async def handle_attachment(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = (
                update.message.from_user.username or update.message.from_user.first_name
        )
        documents = []
        if update.message.document:
            file_id = update.message.document.file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path
            message_file = MessageFile(name=update.message.document.file_name, url=file_path)
            documents.append(message_file)

        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = str(update.message.reply_to_message.message_id)

        message = Message(
            message_id=str(update.message.message_id),
            message=update.message.caption or "",
            chat_id=str(update.message.chat_id),
            user_id=str(update.message.from_user.id),
            username=username,
            timestamp=update.message.date,
            messanger=MessangerEnum.telegram,
            reply_to_id=reply_to_id,
            documents=documents,
        )
        await self.new_message(message=message)

    async def handle_start(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        help_message = """Выбери себе никнейм с помощью команды /nickname <твой ник>
Когда будешь готов(а) к общению, жми /connect"""
        await update.effective_message.reply_text(help_message)

    async def handle_connect(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self.storage.is_banned(chat_id=str(update.message.chat_id)):
            if self.settings.moderation:
                self.storage.moderate(chat_id=str(update.message.chat_id))
                bot = Bot(self.settings.token)
                for chat_id in self.settings.admin_chats:
                    await bot.send_message(
                        chat_id=chat_id, text=f"Модерация {update.message.chat_id}"
                    )

                await update.effective_message.reply_text("Модерация")
            else:
                self.storage.connect(source_chat_id=str(update.message.chat_id))
                await update.effective_message.reply_text("Ok")

    async def handle_disconnect(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.storage.disconnect(source_chat_id=str(update.message.chat_id))
        await update.effective_message.reply_text("Ok")

    async def handle_ban(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if str(update.effective_user.id) not in self.settings.admin_chats:
            return None

        for chat_id in context.args:
            self.storage.ban(chat_id=chat_id)
            await update.effective_message.reply_text(f"Ok {chat_id}")

    async def handle_unban(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if str(update.effective_user.id) not in self.settings.admin_chats:
            return None

        for chat_id in context.args:
            self.storage.unban(chat_id=chat_id)
            await update.effective_message.reply_text(f"Ok {chat_id}")

    async def handle_list_of_users(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if str(update.effective_user.id) not in self.settings.admin_chats:
            return None

        users = self.storage.list_of_users()
        users_result = "\n".join(
            [f"{user.chat_id} - {user.nickname}" for user in users]
        )
        if users_result:
            await update.effective_message.reply_text(users_result)
        else:
            await update.effective_message.reply_text("No users")

    async def handle_on_moderation(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if str(update.effective_user.id) not in self.settings.admin_chats:
            return None

        users = self.storage.list_of_moderation()
        users_result = "\n".join(
            [f"{user.chat_id} - {user.nickname}" for user in users]
        )
        if users_result:
            await update.effective_message.reply_text(users_result)
        else:
            await update.effective_message.reply_text("No users")

    async def handle_approve(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if str(update.effective_user.id) not in self.settings.admin_chats:
            return None

        bot = Bot(self.settings.token)
        for chat_id in context.args:
            self.storage.approve(chat_id=chat_id)
            await update.effective_message.reply_text(f"Ok {chat_id}")
            await bot.send_message(chat_id=chat_id, text=f"Проходите в вип заааааал")

    async def handle_set_nickname(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            nickname = " ".join(context.args)
            if not nickname:
                await update.effective_message.reply_text("Не хватает аргументов")
                return None

            self.storage.set_nickname(
                author_id=str(update.message.from_user.id), nickname=nickname
            )
            await update.effective_message.reply_text(nickname)
        except IndexError:
            await update.effective_message.reply_text("Не хватает аргументов")

    async def send_message(self, message: Message) -> None:
        output_channels = self.storage.get_recipients(source_chat_id=message.chat_id)

        bot = Bot(self.settings.token)
        for output_channel in output_channels:
            username = self.storage.get_nickname(message.chat_id) or message.username
            message_content = (
                f"{username} [{message.messanger.value}]\n{message.message}"
            )
            try:
                for _message_content in self.message_parts(message_content, max_size=4000):
                    await bot.send_message(
                        chat_id=output_channel,
                        text=_message_content,
                    )

                for image_chunk in self.message_parts(message.images, max_size=10):
                    image_input = [InputMediaPhoto(media=image.url, filename=image.name) for image in image_chunk]
                    if image_input:
                        await bot.send_media_group(
                            chat_id=output_channel, media=image_input
                        )

                for audio_chunk in self.message_parts(message.audios, max_size=10):
                    audio_input = [InputMediaAudio(media=audio.url, filename=audio.name) for audio in audio_chunk]
                    if audio_input:
                        await bot.send_media_group(
                            chat_id=output_channel, media=audio_input
                        )

                for video_chunk in self.message_parts(message.videos, max_size=10):
                    video_input = [InputMediaVideo(media=video.url, filename=video.name) for video in video_chunk]
                    if video_input:
                        await bot.send_media_group(
                            chat_id=output_channel, media=video_input
                        )

                for animation in message.animations:
                    await bot.send_animation(
                        chat_id=output_channel, animation=animation.url,
                    )

                for document_chunk in self.message_parts(message.documents, max_size=10):
                    document_input = [InputMediaDocument(media=document.url, filename=document.name) for document in document_chunk]
                    if document_input:
                        await bot.send_media_group(
                            chat_id=output_channel, media=document_input
                        )

            except Forbidden:
                self.storage.disconnect(source_chat_id=output_channel)
                logger.exception(f"Disconnect {output_channel} because of error")
            except Exception:
                logger.exception("Exception in send_message")

    def message_parts[T](self, message: typing.Iterable[T], max_size: int) -> list[T]:
        parts = []
        while len(message) > max_size:
            parts.append(message[:max_size])
            message = message[max_size:]

        parts.append(message)
        return parts
