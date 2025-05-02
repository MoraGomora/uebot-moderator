from time import sleep
import asyncio

from pyrogram.errors import FloodWait

LENGTH_COUNT = 20

async def type(_, msg) -> str:
    orig_text, text, tbp = "", "", ""
    typing_symbol = "█"

    try:
        if isinstance(msg.text, str):
            orig_text = msg.text.split(".type ", maxsplit=1)[1]
            checker = orig_text.split()
            text = orig_text

        if len(checker) <= LENGTH_COUNT:
            while(tbp != orig_text):
                try:
                    await msg.edit(tbp + typing_symbol)
                    tbp = tbp + text[0]
                    text = text[1:]

                    await msg.edit(tbp)
                    await asyncio.sleep(0.07)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
        else:
            await msg.edit("The message should not be longer than 20 words")
    except IndexError:
        await msg.edit("Please enter text as an argument")
