import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import R_HOST, R_PORT, REPLY_CANCEL, REPLY_DUEL, REPLY_JOIN, REPLY_STATUS, REPLY_START

r = redis.Redis(host=R_HOST, port=R_PORT, db=0)

async def handle_cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👤 My Account", callback_data=f'account-1'),
            InlineKeyboardButton("⚔️ My Challenges", callback_data=f'games'),
        ],
        [
            InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
        ],
        [
            InlineKeyboardButton("🆕 Create new Challenge", callback_data=f'create-1'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(REPLY_START, reply_markup=reply_markup)

async def handle_cmd_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(f'New duel by user {user_id}')
    r.set(f'{user_id}', 'SETTING')
    await update.message.reply_text(REPLY_DUEL)

async def handle_cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_CANCEL)

async def handle_cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_STATUS)

async def handle_cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(f'Join by user {user_id}')
    r.set(f'{user_id}', 'JOINING')
    await update.message.reply_text(REPLY_JOIN)
