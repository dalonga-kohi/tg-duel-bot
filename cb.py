from telegram import Update
from telegram.ext import ContextTypes

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    print(f'User {query.from_user.id} Selected: {query.data}')