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
            InlineKeyboardButton("🆕 Create new Challenge", callback_data=f'create-new'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(REPLY_START, reply_markup=reply_markup)

async def handle_cmd_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    status = r.get(user_id)

    if status:
        await update.message.reply_text('You have started another task before make sure you are not currently joining to some challenge or creating one.')
        return

    print(f'New duel by user {user_id}')
    r.set(f'{user_id}', 'SETTING')
    keyboard = [
        [InlineKeyboardButton("❌ Cancel Challenge", callback_data=f'abandon-nogame')],
    ]
    await update.message.reply_text(REPLY_DUEL, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def handle_cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    status = r.get(user_id)
    if status:
        await update.message.reply_text('You have started another task before make sure you are not currently joining to some challenge or creating one.')
        return

    r.set(f'{user_id}', 'STATUS')
    await update.message.reply_text(REPLY_STATUS)

async def handle_cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(f'Join by user {user_id}')
    status = r.get(user_id)

    if status:
        await update.message.reply_text('You have started another task before make sure you are not currently joining to some challenge or creating one.')
        return

    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-nogame')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    r.set(f'{user_id}', 'JOINING')
    await update.message.reply_text(REPLY_JOIN, reply_markup=reply_markup)
