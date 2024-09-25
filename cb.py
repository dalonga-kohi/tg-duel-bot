import time
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import REPLY_DUEL, REPLY_GAME_END, REPLY_START, RULES, T_GAME, MINT, DECIMALS, TOKEN_NAME
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT
import redis
from solders.keypair import Keypair # type: ignore
import mysql.connector
from solana.rpc.api import Client
from solders.pubkey import Pubkey # type: ignore
from solana.rpc.types import TokenAccountOpts
from timer import set_player_timer, set_start_game_timer
from group import send_group_msg
from grouptypes import MsgType
from refounds import abandon_game, cancel, stop_join, withdraw
from status import show_games_canceled, show_games_lost, show_games_won, show_status, show_games_pending

bombo_mint_address = Pubkey.from_string(MINT)

r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    print(f'User {query.from_user.id} Selected: {query.data} in chat {chat_id}')
    arg = query.data.split('-')[0]
    mydb.commit()


    if arg == 'wd':
        status = r.get(user_id)

        if status:
            await context.bot.send_message(chat_id=chat_id, text='You have started another task before make sure you are not currently joining to some gulag or creating one.')
            return

        r.set(user_id, "WD")
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data=f'canaccount-1')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="<b>You are withdrawing refound balance from your account(There is no way back if you enter the address)</b>\n\nEnter your SOL wallet address:", parse_mode='HTML', reply_markup=reply_markup)
    elif arg == "withd":
        status = r.get(user_id)

        if status:
            await context.bot.send_message(chat_id=chat_id, text='You have started another task before make sure you are not currently joining to some gulag or creating one.')
            return

        r.set(user_id, "WITHD")
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data=f'canaccount-1')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="<b>You are withdrawing whole balance from your prize pool(There is no way back if you enter the address)</b>\n\nEnter your SOL wallet address:", parse_mode='HTML', reply_markup=reply_markup)

    elif arg == 'canaccount':
        status = r.get(user_id)

        if not status or (status != 'WD' and status != 'WITHD'):
            print(status, "not status")
            return

        r.delete(user_id)
        await show_account(user_id, context)

    elif arg == 'confirm':
        await confirm(chat_id=chat_id, query=query, user_id=user_id,context=context, update=update)

    elif arg == 'abandon':
        game_id = query.data.split('-')[1]
        print('abandon')
        await abandon_game(chat_id=chat_id, context=context,query=query,game_id=game_id, user_id=user_id)

    elif arg == 'create':
        status = r.get(user_id)

        if status:
            await context.bot.send_message(chat_id=chat_id, text='You have started another task before make sure you are not currently joining to some gulag or creating one.')
            return

        print(f'New duel by user {user_id}')
        r.set(f'{user_id}', 'SETTING')
        keyboard = [
            [InlineKeyboardButton("❌ Cancel Gulag", callback_data=f'abandon-nogame')],
        ]
        await context.bot.send_message(chat_id=chat_id, text=REPLY_DUEL, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

    elif arg == 'status':
        game_id = query.data.split('-')[1]
        await show_status(game_id, context, chat_id)

    elif arg == 'games':
        msg_id = query.message.message_id
        keyboard = [
            [InlineKeyboardButton("🏆 Won Gulags", callback_data=f'won-1')],
            [InlineKeyboardButton("🔃 Pending Gulags", callback_data=f'pending-1')],
            [InlineKeyboardButton("💀 Lost Gulags", callback_data=f'lost-1')],
            [InlineKeyboardButton("❌ Canceled Gulags", callback_data=f'gcanceled-1')],
            [InlineKeyboardButton("🔙 Go back", callback_data=f'back-{msg_id}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="What type of gulag are you looking for?", reply_markup=reply_markup, parse_mode='HTML')

    elif arg == 'account':
        await show_account(user_id, context)

    elif arg == 'stopj':
        game_id = query.data.split('-')[1]
        await stop_join(chat_id=chat_id, context=context,game_id=game_id, user_id=user_id)

    elif arg == 'cancel':
        game_id = query.data.split('-')[1]
        await cancel(chat_id=chat_id, context=context,game_id=game_id, user_id=user_id)

    elif arg == 'rules':
        keyboard = [
            [
                InlineKeyboardButton("👤 My Account", callback_data=f'account-1'),
                InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
            ],
            [
                InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
            ],
            [
                InlineKeyboardButton("🆕 Create new Gulag", callback_data=f'create-new'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=RULES, parse_mode='MarkdownV2', reply_markup=reply_markup)

    elif arg == 'pending':
        print('Show pending gulags')
        await show_games_pending(user_id=user_id, context=context)
    elif arg == 'won':
        await show_games_won(user_id=user_id, context=context)
    elif arg == 'lost':
        await show_games_lost(user_id=user_id, context=context)
    elif arg == 'gcanceled':
        await show_games_canceled(user_id=user_id, context=context)
    elif arg == 'back':
        keyboard = [
            [
                InlineKeyboardButton("👤 My Account", callback_data=f'account-1'),
                InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
            ],
            [
                InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
            ],
            [
                InlineKeyboardButton("🆕 Create new Gulag", callback_data=f'create-new'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg_id = query.data.split('-')[1]
        await context.bot.send_message(chat_id=chat_id, text=REPLY_START, reply_markup=reply_markup, parse_mode='MarkdownV2')

    await query.answer()

def check_balance(pub_key: str) -> float:
    client = Client("https://api.mainnet-beta.solana.com")
    # sender_token_account = get_associated_token_address(Pubkey.from_string(pub_key), bombo_mint_address)
    # token_balance_response = client.get_token_account_balance(sender_token_account)
    # token_balance = token_balance_response
    pub_key = Pubkey.from_string(pub_key)
    for attempt in range(2):
        try:
            balance = client.get_balance(pub_key)
            print(f"Address: {pub_key}")
            print(f"SOL Balance: {balance.value / (10**DECIMALS)} SOL")
            token_accounts = client.get_token_accounts_by_owner(pub_key, TokenAccountOpts(mint=bombo_mint_address))
            if not token_accounts.value:
                token_balance = 0
            else:
                token_balance = client.get_token_account_balance(token_accounts.value[0].pubkey).value.amount
                if not token_balance:
                    token_balance = 0
                token_balance = float(token_balance)/ (10**DECIMALS)

            print(f'BOMBO Balance: {token_balance} ${TOKEN_NAME}')

            return token_balance
        except:
            print("Failed to retrive balance")
            time.sleep(1)
    return 0






async def confirm(user_id: int, query: CallbackQuery | None, chat_id, update, context):
    status = r.get(user_id)
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )

    if not status:
        await query.answer()
        return

    if not "DEPOSIT" in status:
        await query.answer()
        return

    mycursor = mydb.cursor()
    status = query.data.split('-')[1]

    if status == 'create':
        game_id = query.data.split('-')[2]
    else:
        game_id = status

    mydb.commit()
    mycursor.execute(f"SELECT stake,status,p1,p2,p3,p4,p5 FROM games WHERE game_id='{game_id}' AND (status=9 OR status=1 OR status=2)")
    myresult = mycursor.fetchall()


    keyboard = [
        [
            InlineKeyboardButton("👤 My Account", callback_data=f'account-1'),
            InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
        ],
        [
            InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
        ],
        [
            InlineKeyboardButton("🆕 Create new Gulag", callback_data=f'create-new'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if not myresult:
        await context.bot.send_message(chat_id=chat_id, text=REPLY_GAME_END, reply_markup=reply_markup)
        r.delete(user_id)
        return
    stake = myresult[0][0]
    g_status = myresult[0][1]
    players = myresult[0][2:]

    mycursor.execute(f"SELECT pub_key, priv_key FROM wallets WHERE game_id='{game_id}' AND user_id='{user_id}'")
    myresult = mycursor.fetchall()
    if not myresult:
        await context.bot.send_message(chat_id=chat_id, text=REPLY_GAME_END, reply_markup=reply_markup)
        r.delete(user_id)
        await query.answer()
        return

    pub_key = myresult[0][0]
    await context.bot.send_message(chat_id=chat_id, text='Looking for your account details... 🔍')
    balance = check_balance(pub_key)

    if int(balance) != int(stake):
        if status == 'create':
            keyboard = [
                [
                    InlineKeyboardButton("💸 Confirm Deposit", callback_data=f'confirm-create-{game_id}'),
                    InlineKeyboardButton("❌ Cancel", callback_data=f'abandon-{game_id}')
                ],
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("💸 Confirm Deposit", callback_data=f'confirm-{game_id}'),
                    InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-{game_id}')
                ],
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=chat_id, text=f'Current balance of the deposit address is <strong>{balance} ${TOKEN_NAME}</strong>.\nSadly it is not correct 😞\n\n\nYour deposit address is:\n<code class="monospace-text">{pub_key}</code>\n \n \nSend EXACTLY <b>{stake} ${TOKEN_NAME}</b> to this address.\nThen tap <strong>"Confirm Deposit"</strong> to begin.', parse_mode='HTML', reply_markup=reply_markup)
        mydb.shutdown()

        return

    keyboard = [
        [
            InlineKeyboardButton("👀 Check Status", callback_data=f'status-{game_id}'),
            InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
        ],
        [
            InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
            InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
        ],
        [
            InlineKeyboardButton("❌ Quit Game", callback_data=f'cancel-{game_id}'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    count = 0
    for p in players:
        if p:
            count = count + 1

    print(f"Count: {count}")

    current_jobs = context.job_queue.get_jobs_by_name(f"start-{game_id}")

    if not current_jobs and count > 1:
        await set_start_game_timer(update=update, context=context, due=T_GAME, text="5 min timer start", job_name=f'start-{game_id}', game_id=game_id)
        print(f"CB: {game_id}")
        await send_group_msg(msg_type=MsgType.BEGIN_JOIN, context=context, user_id=user_id, game_id=game_id, stake=stake, count=count)
    else:
        await send_group_msg(msg_type=MsgType.BEGIN_JOIN, context=context, user_id=user_id, game_id=game_id, stake=stake, count=count)

    mydb.commit()

    if g_status == 9:
        mycursor.execute(f"UPDATE games SET status=1 WHERE game_id='{game_id}' AND p1='{user_id}'")
        await send_group_msg(msg_type=MsgType.START, context=context, user_id=user_id, game_id=game_id, stake=stake)

    mydb.commit()

    await context.bot.send_message(chat_id=chat_id, text=f'✅ <strong>Success!</strong>\n\n Your game id is: <code class="monospace-text">{game_id}</code>\n\nYou can share it with your friends and wait for the start', reply_markup=reply_markup, parse_mode='HTML')
    r.delete(user_id)
    mydb.shutdown()



async def show_account(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )
    mydb.commit()
    keyboard = [
        [
        InlineKeyboardButton("🏦 Withdraw", callback_data=f'withd-1'),
        InlineKeyboardButton("🔙 Go back", callback_data=f'back-1'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT pub_key, lost, won, total, withdraw FROM accounts WHERE user_id={user_id}")
    results = mycursor.fetchall()
    if not results:
        keypair = Keypair()
        public_key = keypair.pubkey()
        private_key = keypair.secret()

        sql = "INSERT INTO accounts(user_id, pub_key,priv_key) VALUES (%s,%s,%s)"
        val = (user_id, f'{public_key}', f'{private_key.hex()}')
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.shutdown()

        lost = 0
        won = 0
        total = 0
        balance = 0
        ref_bal = 0
    else:
        public_key = results[0][0]
        lost = results[0][1]
        won = results[0][2]
        total = results[0][3]
        balance = results[0][4]

        ref_bal = check_balance(public_key)

    msg = f"🏆 Gulags Won: {won}\t\t 💀 Gulags Lost: {lost}\n\nTotal Prize: {total} ${TOKEN_NAME}\n\nFunds to withdraw: {balance} ${TOKEN_NAME}"

    await context.bot.send_message(chat_id=user_id, text=msg, reply_markup=reply_markup)