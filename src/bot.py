from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN
from .database import Database

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.db = Database()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("add", self.add_command))
        self.application.add_handler(CommandHandler("all", self.all_command))
        self.application.add_handler(CommandHandler("remove", self.remove_command))
        self.application.add_handler(CommandHandler("list", self.list_command))

    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Добавление участников в группу
        Использование: /add @user1 @user2 @user3
        """
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("Эта команда работает только в группах!")
            return

        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите username'ы участников.\n"
                "Пример: /add @user1 @user2 @user3"
            )
            return

        chat_id = update.effective_chat.id
        chat_name = update.effective_chat.title

        self.db.add_group(chat_id, chat_name)

        added, failed = self.db.add_members(chat_id, context.args)

        response = [f"✅ Добавлено участников: {added}"]
        if failed:
            response.append(f"❌ Не удалось добавить: {', '.join(failed)}")

        await update.message.reply_text("\n".join(response))

    async def all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отметить всех участников группы"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("Эта команда работает только в группах!")
            return

        try:
            chat_id = update.effective_chat.id
            sender_username = update.effective_user.username

            # Получаем всех участников из базы
            members = self.db.get_group_members(chat_id)

            # Исключаем отправителя
            if sender_username:
                members_to_mention = members - {sender_username}
            else:
                members_to_mention = members

            # Формируем сообщение
            if members_to_mention:
                mentions = " ".join(f"@{username}" for username in sorted(members_to_mention))
                message = f"🔔 {mentions}"
            else:
                message = "❌ В базе нет участников для упоминания"

            await update.message.reply_text(message)

        except Exception as e:
            print(f"Error in all_command: {e}")
            await update.message.reply_text("Произошла ошибка при отправке сообщения.")

    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Удаление участника из группы
        Использование: /remove @username
        """
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("Эта команда работает только в группах!")
            return

        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите username участника.\n"
                "Пример: /remove @username"
            )
            return

        username = context.args[0]
        chat_id = update.effective_chat.id

        if self.db.remove_member(chat_id, username):
            await update.message.reply_text(f"✅ Участник {username} удален из базы")
        else:
            await update.message.reply_text(f"❌ Не удалось удалить участника {username}")

    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список всех участников в базе"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("Эта команда работает только в группах!")
            return

        chat_id = update.effective_chat.id
        members = self.db.get_group_members(chat_id)

        if members:
            member_list = "\n".join(f"@{username}" for username in sorted(members))
            await update.message.reply_text(
                f"📋 Список участников в базе ({len(members)}):\n{member_list}"
            )
        else:
            await update.message.reply_text("📋 В базе нет участников для этой группы")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для оповещения всех участников группы.\n\n"
            "Доступные команды:\n"
            "/add @user1 @user2 - добавить участников\n"
            "/remove @user - удалить участника\n"
            "/all - отметить всех участников\n"
            "/list - показать список участников"
        )

    def run(self):
        """Запуск бота"""
        print("Bot starting...")
        self.application.run_polling()