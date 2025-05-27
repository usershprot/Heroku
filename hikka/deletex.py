# meta developer: @usershprot
# meta banner: https://placehold.co/600x200/222/fff?text=AntiDeleteX
# meta pic: https://placehold.co/100x100/222/fff?text=AD

from .. import loader, utils
from telethon import events

@loader.tds
class AntiDeleteXMod(loader.Module):
    """Восстанавливает удалённые сообщения"""
    strings = {"name": "AntiDeleteX"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("log_chat", None, "Куда кидать удалённые сообщения (chat_id)"),
            loader.ConfigValue("watch_others", False, "Восстанавливать не только свои сообщения")
        )
        self.cache = {}

    async def client_ready(self, client, db):
        self.client = client

        @client.on(events.MessageEdited)
        async def handle_edit(event):
            if not event.message or not event.message.text:
                return
            self.cache[event.message.id] = event.message

        @client.on(events.MessageDeleted)
        async def handle_delete(event):
            for msg_id in event.deleted_ids:
                msg = self.cache.get(msg_id)
                if not msg: continue
                if not self.config["watch_others"] and msg.sender_id != (await client.get_me()).id:
                    continue

                text = msg.raw_text or "<медиа>"
                sender = (await msg.get_sender()).first_name
                dest = self.config["log_chat"] or "me"

                try:
                    await msg.forward_to(dest)
                    await client.send_message(dest, f"❌ *Удалено сообщение*\n👤 От: {sender}\n📝 Текст: {text}")
                except:
                    pass

    async def adxsetlogcmd(self, message):
        """Установить лог-чат: .adxsetlog -1001234567890"""
        args = utils.get_args(message)
        if not args:
            return await message.edit("Укажи ID или @лог-чат")
        self.config["log_chat"] = args[0]
        await message.edit(f"✅ Лог-чат установлен: {args[0]}")

    async def adxtogglecmd(self, message):
        """Включить/выключить слежку за чужими сообщениями"""
        self.config["watch_others"] = not self.config["watch_others"]
        state = "включена" if self.config["watch_others"] else "отключена"
        await message.edit(f"✅ Слежка за чужими сообщениями {state}")