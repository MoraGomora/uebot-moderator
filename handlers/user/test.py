async def test(client, msg):
    try:
        await client.send_message(msg.chat.id, f"You say: {msg.text.split(".test ", maxsplit=1)[1]}")
    except IndexError:
        await msg.edit("Please enter a text")