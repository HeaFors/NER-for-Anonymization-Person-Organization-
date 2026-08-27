import os
import logging
from dotenv import load_dotenv  # <-- 1. Додали імпорт
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from mcp_server import run_agent_tool

load_dotenv()  # <-- 2. Автоматично зчитує файл .env

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я AI-асистент. Запитай мене про студентів або попроси знайти сутності в тексті."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    agent_response = run_agent_tool(user_text)

    await update.message.reply_text(
        text=agent_response,
        parse_mode="Markdown"
    )


if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не знайдено в змінних оточення (.env)!")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram Bot запущено через MCP шар...")
    app.run_polling()