import asyncio
import random
import logging
import os
from dotenv import load_dotenv

# ensure event loop exists before ptb initialises (required on Python 3.12+)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

logging.basicConfig(level=logging.INFO)

HELP_TEXT = (
    "Команды:\n"
    "/triple — случайное 3-значное число (100–999)\n"
    "/quadruple — случайное 4-значное число (1000–9999)\n"
    "/quintuple — случайное 5-значное число (10000–99999)\n"
    "/random — случайное число до 1 000 000\n"
    "/random 500 — случайное число от 0 до 500\n"
    "/random 10 20 — случайное число от 10 до 20"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я генерирую случайные числа.\n\n" + HELP_TEXT)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def triple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(100, 999)))


async def quadruple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(1000, 9999)))


async def quintuple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(10000, 99999)))


async def rand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    try:
        if not args:
            lo, hi = 0, 1_000_000
        elif len(args) == 1:
            lo, hi = 0, int(args[0])
        else:
            lo, hi = int(args[0]), int(args[1])
    except ValueError:
        await update.message.reply_text("Использование: /random, /random 500, /random 10 20")
        return

    if lo > hi:
        lo, hi = hi, lo

    await update.message.reply_text(str(random.randint(lo, hi)))


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("triple", triple))
    app.add_handler(CommandHandler("quadruple", quadruple))
    app.add_handler(CommandHandler("quintuple", quintuple))
    app.add_handler(CommandHandler("random", rand))

    app.run_polling()
