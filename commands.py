import redis
from telegram import Update
from telegram.ext import ContextTypes
from config import R_HOST, R_PORT, REPLY_CANCEL, REPLY_DUEL, REPLY_JOIN, REPLY_STATUS, REPLY_START

r = redis.Redis(host=R_HOST, port=R_PORT, db=0)

async def handle_cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_START)

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
