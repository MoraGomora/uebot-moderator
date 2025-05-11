from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus

from enums import CommandAccessLevel
from config.config import get_owner_id

DEVS = []

def check_access_control(access_level: CommandAccessLevel):
    async def func(_, client, query):
        owner_id = int(get_owner_id())

        if getattr(query.from_user, "is_bot", False):
            return False
        if getattr(getattr(query, "forward_from", None), "is_bot", False):
            return False
            
        if query.chat.type in [ChatType.CHANNEL, ChatType.BOT]:
            return False

        if access_level == CommandAccessLevel.USER:
            if not getattr(query.from_user, "is_self", False):
                await query.reply("To use this command, you must be logged in (authorization is not currently available)")
                return False
            return True
            
        elif access_level == CommandAccessLevel.PRIVATE:
            user_id = int(getattr(query.from_user, "id", None))

            if owner_id != user_id:
                return False
            
            if len(DEVS) != 0:
                for dev in DEVS:
                    if not int.is_integer(dev):
                        print("The DEVS list has a different value, not int")
                        return False
                    if user_id != dev:
                        return False
            
            return True
            
        elif access_level == CommandAccessLevel.PUBLIC:
            try:
                if query.chat.id == owner_id:
                    return False
                
                user = await client.get_chat_member(query.chat.id, owner_id)

                if user is None:
                    return False
                if not query.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                    return False

                return True
            except Exception as e:
                await client.send_message(query.chat.id, f"Something was happened: {e}")
                return False

    return filters.create(func)

async def is_admin(_, client, query):
    try:
        if query.chat.id == query.from_user.id:
            return False
        
        user = await client.get_chat_member(query.chat.id, query.from_user.id)

        if user.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
    except Exception as e:
        await client.send_message(query.chat.id, f"Something was happened: {e}")
        return False
    
    print(user)

is_admin = filters.create(is_admin)