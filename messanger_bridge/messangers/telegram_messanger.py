import asyncio
import contextlib
import logging

from telegram import Update, Bot
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)

from messangers.abstract_messanger import AbstractMessanger
from models.message import Message, MessangerEnum

logger = logging.getLogger(__name__)

class TelegramMessanger(AbstractMessanger):

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def process_messages():
            application = Application.builder().token(self.settings.token).build()

            application.add_handler(
                MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
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

    async def handle_message(
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
                f"От {username} из {message.messanger.value}: {message.message}"
            )
            try:
                for _message_content in self.message_parts(message_content):
                    await bot.send_message(
                        chat_id=output_channel,
                        text=message_content,
                    )
            except Exception:
                self.storage.disconnect(source_chat_id=output_channel)
                logger.info(f"Disconnect {output_channel} because of error")

    def message_parts(self, message: str) -> list[str]:
        parts = []
        while len(message) > 4000:
            parts.append(message[:4000])
            message = message[4000:]

        parts.append(message)
        return parts
