from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN
from .database import Database

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.db = Database()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(MessageHandler(filters.StatusUpdate.CHAT_CREATED | filters.StatusUpdate.MIGRATE | filters.StatusUpdate.NEW_CHAT_MEMBERS, self.on_join))
        
        from telegram.ext import ChatMemberHandler
        self.application.add_handler(ChatMemberHandler(self.on_chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))

        self.application.add_handler(CommandHandler("all", self.all_command))
        self.application.add_handler(MessageHandler(filters.Regex(r"^@all$"), self.all_command))
        
        self.application.add_handler(MessageHandler(filters.TEXT | filters.StatusUpdate.NEW_CHAT_MEMBERS, self.capture_user))

    async def on_join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
            
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                await update.message.reply_text(
                    "Привет! 👋\n\n"
                    "Я бот для уведомления всех участников.\n"
                    "❗❗ Важно: Чтобы я мог запоминать участников и уведомлять их, "
                    "сделайте меня администратором группы пж."
                )

    async def on_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = update.chat_member
        
        if result.new_chat_member.status == "administrator":
            chat_id = update.effective_chat.id
            
            try:
                admins = await context.bot.get_chat_administrators(chat_id)
                count = 0
                for admin in admins:
                    if not admin.user.is_bot:
                        self.db.register_user(
                            group_id=chat_id,
                            user_id=admin.user.id,
                            username=admin.user.username,
                            first_name=admin.user.first_name
                        )
                        count += 1 
            except Exception as e:
                print(f"Error fetching admins: {e}")


    async def capture_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return

        user = update.effective_user
        chat = update.effective_chat
        
        if user and not user.is_bot:
            self.db.register_user(
                group_id=chat.id,
                user_id=user.id,
                username=user.username,
                first_name=user.first_name
            )
            
        if update.message and update.message.new_chat_members:
            for member in update.message.new_chat_members:
                if not member.is_bot:
                    self.db.register_user(
                        group_id=chat.id,
                        user_id=member.id,
                        username=member.username,
                        first_name=member.first_name
                    )

    async def all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("Эта команда работает только в группах!")
            return

        chat_id = update.effective_chat.id
        
        try:
            await update.message.delete()
        except Exception:
            pass

        users = self.db.get_group_users(chat_id)
        
        if not users:
            msg = await context.bot.send_message(chat_id, "Я пока никого не запомнил. Пусть участники напишут что-нибудь в чат.")
            return

        mentions = []
        for user in users:
            mentions.append(f'<a href="tg://user?id={user["user_id"]}">\u200b</a>')

        chunk_size = 50
        for i in range(0, len(mentions), chunk_size):
            chunk = mentions[i:i + chunk_size]
            hidden_mentions_str = "".join(chunk)
            
            text = f"🔔 <b>Внимание всем!</b>{hidden_mentions_str}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML
            )

    def run(self):
        print("Bot starting...")
        self.application.run_polling()
