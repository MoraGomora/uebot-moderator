from pyrogram import Client, filters

from utils.json_manager import JSONManager

async def register(client: Client):
    @client.on_message(filters.command("test", prefixes="."))
    async def test(client, msg):
        json = JSONManager("test")
        await client.send_message(msg.chat.id, msg.text)
        await json.write(dict(msg))