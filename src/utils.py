async def get_all_chat_members(chat_id, bot):
    """Получение списка всех участников группы"""
    members = []
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for member in admins:
            if not member.user.is_bot:
                members.append(member)

        chat_info = await bot.get_chat(chat_id)
        if hasattr(chat_info, 'permissions'):
            members_count = chat_info.get_member_count()
            print(f"Total members in chat: {members_count}")
    except Exception as e:
        print(f"Error getting chat members: {e}")
    return members


def create_mention_string(members):
    """Создание строки с упоминаниями всех участников"""
    mentions = []
    for member in members:
        user = member.user
        if user.username:
            mentions.append(f"@{user.username}")
        else:
            mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
    return " ".join(mentions)