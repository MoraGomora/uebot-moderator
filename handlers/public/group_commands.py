from utils.messages import format_message_info

async def message_data(client, msg):
    reply_message = getattr(msg, "reply_to_message", None)

    if reply_message is None:
        return
    
    await client.send_message(format_message_info(reply_message))