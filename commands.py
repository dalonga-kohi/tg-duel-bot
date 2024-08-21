import redis
from telegram import Update
from telegram.ext import ContextTypes
from config import R_HOST, R_PORT, REPLY_CANCEL, REPLY_DUEL, REPLY_STATUS, REPLY_START
import random

r = redis.Redis(host=R_HOST, port=R_PORT, db=0)

async def handle_cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_START)

async def handle_cmd_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    game_id = r.get(f'user-{user_id}')
    print(f'New duel by user {user_id}')
    if not game_id:
        await update.message.reply_text(REPLY_DUEL)
        id = create_game_id()
        r.set(f'user-{user_id}', id)
        r.set(id, 'SETTING')
    else:
        await update.message.reply_text('Sorry 😓, you are already in a game.')


async def handle_cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_CANCEL)

async def handle_cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_STATUS)

async def handle_cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_STATUS)

def create_game_id() -> str:
    while True:
        id = random.randint(1234,9999999)
        id = f'game-{id}'
        game = r.get(id)

        print('creating new game')

        if not game:
            return id
        else:
            continue
