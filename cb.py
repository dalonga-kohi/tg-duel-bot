from telegram import Update
from telegram.ext import ContextTypes

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    print(f'User {query.from_user} Selected: {query}')

    # await update.message.reply_text(f"Selected: {query}")