from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application, MessageHandler
from commands import handle_cmd_duel, handle_cmd_start, handle_cmd_help
from config import CMD_DUEL, TOKEN, BOT_USERNAME, CMD_START, CMD_HELP, REPLY_START
import redis

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error: \n {context.error}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    proc = update.message.text.lower().strip()
    user_id = update.message.from_user.id




if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler(CMD_START, handle_cmd_start))
    app.add_handler(CommandHandler(CMD_DUEL, handle_cmd_duel))
    app.add_handler(CommandHandler(CMD_HELP, handle_cmd_help))

    app.add_handler(MessageHandler(handle_message))

    app.add_error_handler(handle_error)

    print('Polling...')
    app.run_polling(poll_interval=2)