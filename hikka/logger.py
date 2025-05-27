from .. import loader, utils
import asyncio
import datetime

@loader.tds
class ChatLoggerMod(loader.Module):
    """Логгер входящих сообщений с отправкой их в отдельный чат-лог"""
    strings = {"name": "ChatLogger"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("log_chat_id", None, "ID чата для логов (будет создан автоматически)")
        )
        self.log_chat = None

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.log_chat = self.config["log_chat_id"]

        if not self.log_chat:
            # Создаем чат с самим собой для логов
            dialogs = await client.get_dialogs()
            for d in dialogs:
                if d.is_user and d.entity.id == (await client.get_me()).id:
                    self.log_chat = d.entity.id
                    break
            self.config["log_chat_id"] = self.log_chat
            await db.set(__name__, "log_chat_id", self.log_chat)

    async def watcher(self, message):
        if message.out:
            return  # игнорируем свои сообщения

        if not self.log_chat:
            return

        sender = await message.get_sender()
        sender_name = sender.first_name or "Unknown"
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat = await message.get_chat()
        chat_name = getattr(chat, "title", str(chat.id))

        text = message.raw_text or "<медиа/файл>"

        log_text = f"[{dt}] [{chat_name}] {sender_name}: {text}"

        try:
            await self.client.send_message(self.log_chat, log_text)
        except Exception:
            pass

    async def setlogchatcmd(self, message):
        """Установить ID чата для логов вручную: .setlogchat -100123456789"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("Укажи ID чата")
        self.config["log_chat_id"] = int(args)
        self.log_chat = int(args)
        await message.edit(f"Лог-чат установлен: {args}")