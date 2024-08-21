from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application, MessageHandler, filters
from commands import handle_cmd_duel, handle_cmd_join, handle_cmd_start, handle_cmd_cancel, handle_cmd_status
from config import CMD_DUEL, R_HOST, R_PORT, REPLY_NO_GAME, REPLY_WRONG_STAKE, TOKEN, CMD_START, CMD_CANCEL, CMD_JOIN, CMD_STATUS
import redis
import mysql.connector

r = redis.Redis(host=R_HOST, port=R_PORT, db=0)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error: \n {context.error}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proc: str = update.message.text.lower().strip()
    user_id = update.message.from_user.id
    game_id = r.get(f'user-{user_id}')
    stake = 0
    status = r.get(game_id)
    status = str(status)
    print(f'User {user_id} sends a message\nGame: {game_id}' )
    print(f'status: {status}')
    if status == 'SETTING':
        try:
            stake = int(proc)
            print(f'Stake: {stake}')
        except:
            await update.message.reply_text(REPLY_WRONG_STAKE)
            return

        r.set(game_id, 'JOINING')
        game_id = game_id.split('-')
        await update.message.reply_text(f'Nice, Your game id is:\n <code>{game_id[1]}</code>\nYou can share it with your frens and wait for the start😊\nCheck status of your game with /status')
        return

    # if not game_id:
    #     await update.message.reply_text(REPLY_NO_GAME)
    #     return




if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler(CMD_START, handle_cmd_start))
    app.add_handler(CommandHandler(CMD_DUEL, handle_cmd_duel))
    app.add_handler(CommandHandler(CMD_CANCEL, handle_cmd_cancel))
    app.add_handler(CommandHandler(CMD_STATUS, handle_cmd_status))
    app.add_handler(CommandHandler(CMD_JOIN, handle_cmd_join))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(handle_error)

    print('Polling...')
    app.run_polling(poll_interval=2)