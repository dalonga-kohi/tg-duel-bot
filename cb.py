from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import REPLY_GAME_END, RULES
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT
import redis
import mysql.connector
from solana.rpc.api import Client
from solana.transaction import Transaction
from solders.pubkey import Pubkey # type: ignore
from solders.keypair import Keypair # type: ignore
from spl.token.instructions import transfer, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import TokenAccountOpts
from timer import set_player_timer, set_start_game_timer

bombo_mint_address = Pubkey.from_string("D3pmeo4MrV2eWMJH3WybR4fnKdMiSS4DrYHqdYNNjQU5")
mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)
r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    print(f'User {query.from_user.id} Selected: {query.data} in chat {chat_id}')
    arg = query.data.split('-')[0]

    if arg == 'confirm':
        await confirm(chat_id=chat_id, query=query, user_id=user_id,context=context, update=update)


    elif arg == 'abandon':
        pass
    elif arg == 'create':
        pass
    elif arg == 'games':
        pass
    elif arg == 'account':
        pass
    elif arg == 'stopj':
        pass
    elif arg == 'quit':
        pass
    elif arg == 'cancel':
        pass
    elif arg == 'rules':
        await context.bot.send_message(chat_id=chat_id, text=RULES, parse_mode='HTML')


    await query.answer()

def check_balance(pub_key: str) -> float:
    client = Client("https://api.mainnet-beta.solana.com")
    # sender_token_account = get_associated_token_address(Pubkey.from_string(pub_key), bombo_mint_address)
    # token_balance_response = client.get_token_account_balance(sender_token_account)
    # token_balance = token_balance_response
    pub_key = Pubkey.from_string(pub_key)

    balance = client.get_balance(pub_key)
    print(f"SOL Balance: {balance.value / 1e9} SOL")
    token_accounts = client.get_token_accounts_by_owner(pub_key, TokenAccountOpts(mint=bombo_mint_address))
    if not token_accounts.value:
        token_balance = 0
    else:
        token_balance = client.get_token_account_balance(token_accounts.value[0].pubkey).value.amount
        if not token_balance:
            token_balance = 0

    print(f'BOMBO Balance: {token_balance} $BOMBO')

    return int(token_balance)

async def confirm(user_id: int, query: CallbackQuery | None, chat_id, update, context):
    status = r.get(user_id)

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

    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT pub_key, priv_key FROM wallets WHERE game_id='{game_id}' AND user_id='{user_id}'")
    myresult = mycursor.fetchall()

    if not myresult:
        await context.bot.send_message(chat_id=chat_id, text=REPLY_GAME_END)
        await query.answer()
        return

    pub_key = myresult[0][0]
    mycursor.execute(f"SELECT stake FROM games WHERE game_id='{game_id}' AND (status=9 OR status=1)")
    myresult = mycursor.fetchall()

    if not myresult:
        await context.bot.send_message(chat_id=chat_id, text=REPLY_GAME_END)
        await query.answer()
        return
    stake = myresult[0][0]
    balance = check_balance(pub_key)

    if balance != stake:
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

        await context.bot.send_message(chat_id=chat_id, text=f'Current balance of the deposit address is <strong>{balance} $BOMBO</strong>.\nSadly it is not enough 😞\n\n\nYour deposit address is:\n<code class="monospace-text">{pub_key}</code>\n \n \nSend EXACTLY <b>{stake} $BOMBO</b> to this address.\nThen tap <strong>"Confirm Deposit"</strong> to begin.', parse_mode='HTML', reply_markup=reply_markup)
        await query.answer()

        return

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
            InlineKeyboardButton("❌ Cancel Challenge", callback_data=f'cancel-{game_id}'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text=f'✅ <strong>Success!</strong>\n\n Your game id is: <code class="monospace-text">{game_id}</code>\n\nYou can share it with your frens and wait for the start', reply_markup=reply_markup, parse_mode='HTML')
    print(f"CB: {game_id}")
    await set_start_game_timer(update=update, context=context, due=40, text="5 min timer start", job_name=f'start-{game_id}')
    r.delete(user_id)