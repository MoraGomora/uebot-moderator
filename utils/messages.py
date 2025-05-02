def format_message_info(message):
    info = []

    info.append(f"📨 <b>Информация о сообщении</b>")
    info.append(f"🆔 ID: <code>{message.id}</code>")
    info.append(f"👤 Отправитель: {message.from_user.mention if message.from_user else 'Система/бот'}")
    info.append(f"💬 Тип: <code>{message.media.value if message.media else 'text'}</code>")
    info.append(f"📅 Дата: <code>{message.date.strftime('%Y-%m-%d %H:%M:%S')}</code>")

    if message.chat:
        info.append(f"💭 Чат: {message.chat.title or message.chat.first_name}")
        info.append(f"🆔 Чата: <code>{message.chat.id}</code>")

    if message.text:
        text_preview = (message.text[:100] + '...') if len(message.text) > 100 else message.text
        info.append(f"📝 Текст:\n<pre>{text_preview}</pre>")

    if message.reply_to_message:
        info.append(f"↩️ Ответ на сообщение ID: <code>{message.reply_to_message.message_id}</code>")

    return '\n'.join(info)
