from pyrogram import Client, filters

from utils.json_manager import JSONManager

async def register(client: Client):
    @client.on_message(filters.command("flip", prefixes=".") & filters.me)
    async def flip(_, msg) -> str:
        json_manager = JSONManager("letters")
        letter_map = await json_manager.read()

        text = msg.text.split(".flip", maxsplit=1)[1]
        final_str = ""
        for char in text:
            if char in letter_map.keys():
                new_char = letter_map[char]
            else:
                new_char = char
            final_str += new_char
        if text != final_str:
            await msg.edit(final_str)
        else:
            await msg.edit(text)