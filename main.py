from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, Application, MessageHandler, filters, CallbackQueryHandler
from commands import handle_cmd_duel, handle_cmd_join, handle_cmd_start, handle_cmd_cancel, handle_cmd_status
from config import CMD_DUEL, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT, REPLY_ALREADY_WD, REPLY_NO_FREE, REPLY_NO_GAME, REPLY_NO_JOIN, REPLY_WRONG_STAKE, TOKEN, CMD_START, CMD_CANCEL, CMD_JOIN, CMD_STATUS
import redis
import mysql.connector
import random
from solders.keypair import Keypair # type: ignore
from solana.rpc.api import Client
from cb import button

bombo_token_mint = "D3pmeo4MrV2eWMJH3WybR4fnKdMiSS4DrYHqdYNNjQU5"
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

    if status == 'SETTING':
        keyboard = [
            [InlineKeyboardButton("❌ Cancel Challenge", callback_data=f'abandon-{user_id}')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            stake = int(proc)
            print(f'Stake: {stake}')
        except:
            await update.message.reply_text(REPLY_WRONG_STAKE ,reply_markup=reply_markup)
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
        val = (user_id, game_id, public_key, private_key.hex())
        mycursor.execute(sql, val)

        mydb.commit()

        keyboard = [
            [
                InlineKeyboardButton("💸 Confirm Deposit", callback_data=f'confirm-create'),
                InlineKeyboardButton("❌ Cancel Challenge", callback_data=f'abandon-{user_id}')
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f'Your deposit address is:\n<code class="monospace-text">{public_key}</code>\n \n \nTo create the challenge send {stake} $BOMBO to this address.\nThen tap <strong>"Confirm Deposit"</strong> to begin.', reply_markup=reply_markup, parse_mode='HTML')
        r.set(user_id, f'WITHDRAW')
        return

    if 'WITHDRAW' in status:
        keyboard = [
            [
                InlineKeyboardButton("👀 Check Status", callback_data=f'status-{game_id}'),
                InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
            ],
            [
                InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
                InlineKeyboardButton("⚔️ My Challenges", callback_data=f'games'),
            ],
            [
                InlineKeyboardButton("❌ Cancel Challenge", callback_data=f'cancel-{game_id}')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f'✅ <strong>Success!</strong>\n\n Your game id is: <code class="monospace-text">{game_id}</code>\n\nYou can share it with your frens and wait for the start', reply_markup=reply_markup, parse_mode='HTML')
        r.delete(user_id)
        return

    if status == 'JOINING':
        try:
            game_id = int(proc)
            print(f'GAME ID: {game_id}')
        except:
            keyboard = [
                [InlineKeyboardButton("❌ Stop Joining", callback_data=f'stopj-{user_id}')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(REPLY_WRONG_STAKE, reply_markup=reply_markup, parse_mode='HTML')
            return

        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT p1,p2,p3,p4,p5,status,stake FROM games WHERE game_id={game_id}")
        myresult = mycursor.fetchall()

        if not myresult:
            keyboard = [
                [InlineKeyboardButton("❌ Stop Joining", callback_data=f'stopj-{user_id}')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(REPLY_NO_JOIN, parse_mode='HTML', reply_markup=reply_markup)
            return
        myresult = myresult[0]
        print(myresult)

        isFree = False
        p_index = 0
        for x in myresult[:5]:
            try:
                if int(x) == user_id:
                    keyboard = [
                        [
                            InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
                            InlineKeyboardButton("⚔️ My Challenges", callback_data=f'games'),
                        ],
                        [
                            InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
                        ],
                        [
                            InlineKeyboardButton("🆕 Create new Challenge", callback_data=f'create-{user_id}'),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("<strong>You are already in that challenge</strong>\n\n You can still join to other challenges or create another one.", parse_mode='HTML', reply_markup=reply_markup)
                    r.delete(user_id)
                    return
            except:
                pass

            p_index = p_index + 1
            if x == None:
                isFree = True
                break

        if not isFree:
            keyboard = [
                [
                    InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
                    InlineKeyboardButton("⚔️ My Challenges", callback_data=f'games'),
                ],
                [
                    InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
                ],
                [
                    InlineKeyboardButton("🆕 Create new Challenge", callback_data=f'create-{user_id}'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(REPLY_NO_FREE, parse_mode='HTML', reply_markup=reply_markup)
            r.delete(user_id)
            return

        # if myresult[5] == 2:
        #     keyboard = [
        #         [
        #             InlineKeyboardButton("Try Again", callback_data=f'again-{game_id}'),
        #             InlineKeyboardButton("👀 Check Status", callback_data=f'status-{game_id}'),
        #         ],
        #         [
        #             InlineKeyboardButton("🆕 Create new Challenge", callback_data=f'create-{user_id}')
        #         ]
        #     ]
        #     reply_markup = InlineKeyboardMarkup(keyboard)
        #     r.delete(user_id)
        #     await update.message.reply_text(REPLY_ALREADY_WD, parse_mode='HTML', reply_markup=reply_markup)
        #     return

        if myresult[5] == 2:
            keyboard = [
                [
                    InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
                    InlineKeyboardButton("⚔️ My Challenges", callback_data=f'games'),
                ],
                [
                    InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
                ],
                [
                    InlineKeyboardButton("🆕 Create new Challenge", callback_data=f'create-{user_id}'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            r.delete(user_id)
            await update.message.reply_text('<strong>Challenge has already begun.</strong>\n\nNo worries, you can choose one of the options below and start playing 🕹️', parse_mode='HTML', reply_markup=reply_markup)
            return

        keypair = Keypair()

        public_key = keypair.pubkey()

        private_key = keypair.secret()
        print(f"Public Key: {public_key}")
        print(f"Private Key: {private_key.hex()}")

        mycursor = mydb.cursor()
        sql = f"UPDATE games SET p{p_index})='{user_id}'"
        mycursor.execute(sql)
        sql = "INSERT INTO wallets (user_id, game_id, pub_key, priv_key) VALUES (%s, %s, %s, %s)"
        val = (user_id, game_id, public_key, private_key.hex())
        mycursor.execute(sql, val)

        mydb.commit()
        keyboard = [
            [
                InlineKeyboardButton("💸 Confirm Deposit", callback_data=f'confirm-{game_id}'),
                InlineKeyboardButton("❌ Quit", callback_data=f'quit-{game_id}')
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f'Your deposit address is:\n<code class="monospace-text">{public_key}</code>\n \n \nTo join send {myresult[6]} $BOMBO to this address.\nThen tap <strong>"Confirm Deposit"</strong> to begin.\n\n You have 4 minutes to confirm the deposit.', reply_markup=reply_markup, parse_mode='HTML')

        r.set(user_id, "WD")
        return


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
    app.add_handler(CommandHandler(CMD_CANCEL, handle_cmd_cancel))
    app.add_handler(CommandHandler(CMD_STATUS, handle_cmd_status))
    app.add_handler(CommandHandler(CMD_JOIN, handle_cmd_join))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(handle_error)

    print('Polling...')
    app.run_polling(poll_interval=2)