import asyncio
import json
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
from telegram.ext import ApplicationBuilder, ChatMemberHandler, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(level=logging.INFO)

HOW_WORDS = [
    "тихо", "не спеша", "не дыша", "не шиша",
    "не пержа", "не жужжа", "не гроша", "черемша", "не тужа", "лёжа", "дрожа",
    "вороша", "без ковша", "со второго этажа", "без гаража", "без экипажа",
    "без лишнего багажа", "без массажа", "без монтажа", "без камуфляжа",
    "для антуража", "без знания падежа", "без мятежа",
    "в три ножа", "два коржа", "без репортажа", "без стажа",
    "с лицом вождя", "с душой моржа", "с повадкой ежа", "с запахом ржа",
    "без суеты", "почти неслышно", "с лёгкой улыбкой", "с тёплым сердцем",
    "медленно, но верно", "спокойно", "без лишних слов", "с внутренним светом",
    "чуть задумчиво, но ясно", "с мягкой уверенностью", "бережно, как будто впервые",
    "с тихой радостью", "неспешно, наслаждаясь моментом", "с добрым ожиданием",
    "мягко, словно ветер", "светло, как утро", "вдумчиво",
    "с теплом в глазах", "неторопливо, но глубоко", "с лёгкой надеждой",
    "тихо, но наполненно", "с уверенностью в хорошем", "спокойно", "принимая всё",
    "с мягкой верой в лучшее", "чуть мечтательно", "с тихим счастьем",
    "внутренне спокойно", "с ощущением уюта", "с нежной благодарностью",
    "медленно, смакуя жизнь", "с тёплой тишиной внутри",
    "с мягкой уверенностью", "с уверенностью в завтрашнем дне", "черемша",
    "c лёгкой иронией", "ни шиша", "четыре карандаша", 
]

HELP_TEXT = (
    "<b>Команды:</b>\n"
    "/double — случайное 2-значное число (10–99) · <i>дабл</i>\n"
    "/triple — случайное 3-значное число (100–999) · <i>трипл</i>\n"
    "/quadruple — случайное 4-значное число (1000–9999) · <i>квадрипл, четырипл</i>\n"
    "/quintuple — случайное 5-значное число (10000–99999) · <i>квинтипл, пентипл, пятерипл</i>\n"
    "/random — случайное число до 1 000 000\n"
    "/random 500 — случайное число от 0 до 500\n"
    "/random 10 20 — случайное число от 10 до 20\n"
    "/alice — случайный стикер\n"
    "/coffee — кофя · <i>кофе</i>\n"
    "/who — случайный участник чата · <i>черемша, кто...</i>\n"
    "/hurry — черемша · <i>спеша</i>\n"
    "/how — как? · <i>как?, СССР, советский союз, в советском союзе</i>"
)

# cache of sticker file_ids, populated on first /alice call
_alice_stickers: list[str] = []

# persistent chat storage
DATA_FILE = "/app/data/chats.json"


def _load_chats() -> dict:
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_chats(chats: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Привет!</b> Я тихо, спокойно, не спеша, генерирую случайные числа\n\n" + HELP_TEXT,
        parse_mode="HTML",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")


async def double(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(10, 99)))


async def triple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(100, 999)))


async def quadruple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(1000, 9999)))


async def quintuple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(10000, 99999)))


async def how(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = random.sample(HOW_WORDS, 3)
    await update.message.reply_text(", ".join(words))


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


COFFEE_REPLIES = [
    "с печенько",
    "я не я без кофя",
    "тупа я",
    "не могу жить без кофя",
    "кофя это моя жизнь",
    "кофя и без печенько?",
]


async def coffee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(COFFEE_REPLIES))


async def hurry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("черемша")


async def who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
    except Exception:
        return

    humans = [m for m in admins if not m.user.is_bot]
    if not humans:
        return

    member = random.choice(humans)
    name = member.user.full_name
    title = getattr(member, "custom_title", None)
    if title:
        name += f" ({title})"
    await update.message.reply_text(name)


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fires when bot is added/removed from a chat."""
    result = update.my_chat_member
    if not result:
        return
    chat = result.chat
    new_status = result.new_chat_member.status
    chats = _load_chats()
    if new_status in ("member", "administrator"):
        chats[str(chat.id)] = {
            "title": chat.title or chat.full_name or str(chat.id),
            "is_admin": new_status == "administrator",
        }
    elif new_status in ("left", "kicked"):
        chats.pop(str(chat.id), None)
    _save_chats(chats)


async def delete_channel_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.sender_chat:
        return
    allowed_raw = os.getenv("ALLOWED_CHANNEL_ID", "").strip()
    try:
        allowed_id = int(allowed_raw) if allowed_raw else None
    except ValueError:
        allowed_id = None
    if allowed_id and update.message.sender_chat.id == allowed_id:
        return
    try:
        await update.message.delete()
    except Exception:
        pass  # бот не админ или нет прав — молча игнорируем


async def track_chat_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback: register chat on first message if not yet known."""
    if not update.message:
        return
    chat = update.message.chat
    if chat.type == "private":
        return
    chats = _load_chats()
    if str(chat.id) in chats:
        return
    try:
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        is_admin = bot_member.status in ("administrator", "creator")
    except Exception:
        is_admin = False
    chats[str(chat.id)] = {
        "title": chat.title or str(chat.id),
        "is_admin": is_admin,
    }
    _save_chats(chats)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = int(os.getenv("ADMIN_ID", "0"))
    if update.effective_user.id != admin_id:
        return

    chats = _load_chats()
    count = len(chats)
    lines = [f"Чатов: {count}\n"]
    for entry in list(chats.values())[:5]:
        role = "админ" if entry.get("is_admin") else "участник"
        lines.append(f"• {entry['title']} ({role})")
    await update.message.reply_text("\n".join(lines))


async def alice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _alice_stickers
    if not _alice_stickers:
        pack_name = os.getenv("ALICE_STICKER_PACK", "inthenameofAlice")
        sticker_set = await context.bot.get_sticker_set(pack_name)
        _alice_stickers = [s.file_id for s in sticker_set.stickers]
    await update.message.reply_sticker(random.choice(_alice_stickers))


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("double", double))
    app.add_handler(CommandHandler("triple", triple))
    app.add_handler(CommandHandler("quadruple", quadruple))
    app.add_handler(CommandHandler("quintuple", quintuple))
    app.add_handler(CommandHandler("random", rand))
    app.add_handler(CommandHandler("how", how))
    app.add_handler(CommandHandler("alice", alice))
    app.add_handler(CommandHandler("coffee", coffee))
    app.add_handler(CommandHandler("hurry", hurry))
    app.add_handler(CommandHandler("who", who))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_chat_on_message), group=1)

    if os.getenv("DELETE_CHANNEL_MESSAGES", "").lower() in ("1", "true", "yes"):
        app.add_handler(MessageHandler(filters.ALL, delete_channel_messages), group=2)
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)в советском союзе|советский союз|ссср|как\?|^как$"),
        how,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)дабл"),
        double,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)трипл"),
        triple,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)квадрипл|четырипл"),
        quadruple,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)квинтипл|пентипл|пятерипл"),
        quintuple,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)кофе"),
        coffee,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)\bкто\b"),
        who,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)спеша"),
        hurry,
    ))

    app.run_polling()
