from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, Application, MessageHandler, filters, CallbackQueryHandler
from cb import withdraw
from commands import handle_cmd_duel, handle_cmd_join, handle_cmd_start, handle_cmd_status, join
from config import CMD_DUEL, MAX_STAKE, MIN_STAKE, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT, REPLY_NO_FREE, REPLY_NO_GAME, REPLY_NO_JOIN, REPLY_WRONG_STAKE, TOKEN, CMD_START, CMD_CANCEL, CMD_JOIN, CMD_STATUS
import redis
import mysql.connector
import random
from solders.keypair import Keypair # type: ignore
from solana.rpc.api import Client
from cb import button, show_account
from refounds import wd_total
from status import show_status

sol_client = Client("https://api.mainnet-beta.solana.com")
r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)
mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error: \n {context.error}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unproc = update.message.text.strip()
    proc: str = update.message.text.lower().strip()
    user_id = update.message.from_user.id
    type = update.message.chat.type
    stake = 0
    print(f'User {user_id} sends a message({type})' )


    if type != 'private':
        return

    if not r.get(user_id):
        await update.message.reply_text(REPLY_NO_GAME)
        return

    status = r.get(user_id)
    print(f'status: {status}')



    ###########################################
    ###########################################
    ###########################################

    if status == 'WD':
        address = unproc
        res = await withdraw(address, user_id)

        if not res:
            keyboard = [
                [InlineKeyboardButton("❌ Cancel", callback_data=f'canaccount-1')],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("This is not a valid SOL wallet or you have no funds to withdraw\nPlease, try again:" ,reply_markup=reply_markup)
            return
        else:
            r.delete(user_id)
            await update.message.reply_text("✅ Successful Transaction")
            await update.message.reply_text(f'Transaction Signature: <code class="monospace-text">{res}</code>', parse_mode="HTML")
            await show_account(user_id, context)

    elif status == 'WITHD':
        address = unproc
        print("procced")
        res = await wd_total(address, user_id)

        if not res:
            keyboard = [
                [InlineKeyboardButton("❌ Cancel", callback_data=f'canaccount-1')],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("This is not a valid SOL wallet or you have no funds to withdraw\nPlease, try again:" ,reply_markup=reply_markup)
            return
        else:
            r.delete(user_id)
            await update.message.reply_text("✅ Successful Transaction")
            await update.message.reply_text(f'Transaction Signature: <code class="monospace-text">{res}</code>', parse_mode="HTML")
            await show_account(user_id, context)


    elif status == 'SETTING':
        keyboard = [
            [InlineKeyboardButton("❌ Cancel Gulag", callback_data=f'abandon-nogame')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            stake = int(proc)
            print(f'Stake: {stake}')
        except:
            await update.message.reply_text(REPLY_WRONG_STAKE ,reply_markup=reply_markup)
            return

        if stake < MIN_STAKE or stake > MAX_STAKE:
            await update.message.reply_text(f"Stake must be in range of <b>{MIN_STAKE} to {MAX_STAKE}</b> $BOMBO" ,reply_markup=reply_markup, parse_mode='HTML')
            return

        keypair = Keypair()
        game_id = create_game_id()

        public_key = keypair.pubkey()

        private_key = keypair.secret()
        print(f"Public Key: {public_key}")
        print(f"Private Key: {private_key.hex()}")

        mycursor = mydb.cursor()
        sql = "INSERT INTO games (game_id, p1, status, stake) VALUES (%s, %s, %s, %s)"
        val = (game_id, user_id, 9, stake)
        mycursor.execute(sql, val)
        sql = "INSERT INTO wallets (user_id, game_id, pub_key, priv_key) VALUES (%s, %s, %s, %s)"
        val = (user_id, game_id, f'{public_key}', f'{private_key.hex()}')
        mycursor.execute(sql, val)
        mydb.commit()

        keyboard = [
            [
                InlineKeyboardButton("💸 Confirm Deposit", callback_data=f'confirm-create-{game_id}'),
                InlineKeyboardButton("❌ Cancel Gulag", callback_data=f'abandon-{game_id}')
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f'Your deposit address is:\n<code class="monospace-text">{public_key}</code>\n \n \nTo create the gulag send <b>{stake} $BOMBO</b> to this address.\nThen tap <strong>"Confirm Deposit"</strong> to begin.', reply_markup=reply_markup, parse_mode='HTML')
        r.set(user_id, f"DEPOSIT")
        return

    elif status == 'JOINING':
        try:
            game_id = int(proc)
            print(f'GAME ID: {game_id}')
        except:
            keyboard = [
                [InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-nogame')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(REPLY_WRONG_STAKE, reply_markup=reply_markup, parse_mode='HTML')
            return

        await join(game_id=game_id, update=update, user_id=user_id, context=context)

    elif status == 'STATUS':
        try:
            game_id = int(proc)
            print(f'GAME ID: {game_id}')
        except:
            keyboard = [
                [InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-nogame')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(REPLY_WRONG_STAKE, reply_markup=reply_markup, parse_mode='HTML')
            return

        await show_status(game_id,context,user_id)


def create_game_id() -> str:
    mycursor = mydb.cursor()

    mycursor.execute("SELECT game_id FROM games")

    myresult = mycursor.fetchall()
    while True:
        id = random.randint(1234,9999999)

        print('creating new game')

        if id not in myresult:
            return f'{id}'
        else:
            continue

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler(CMD_START, handle_cmd_start))
    app.add_handler(CommandHandler(CMD_DUEL, handle_cmd_duel))
    app.add_handler(CommandHandler(CMD_STATUS, handle_cmd_status))
    app.add_handler(CommandHandler(CMD_JOIN, handle_cmd_join))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(handle_error)

    print('Polling...')
    app.run_polling(poll_interval=2)