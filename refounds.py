import mysql.connector
import redis
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT, REPLY_ABAN, REPLY_GAME_END
from solders.pubkey import Pubkey # type: ignore
from spl.token.instructions import transfer, get_associated_token_address, TransferParams
from solders.keypair import Keypair # type: ignore
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
import base58

from group import send_group_msg
from group import MsgType

bombo_mint_address = Pubkey.from_string("D3pmeo4MrV2eWMJH3WybR4fnKdMiSS4DrYHqdYNNjQU5")

mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)
r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)
mycursor = mydb.cursor()

keyboard = [
    [
        InlineKeyboardButton("👤 My Account", callback_data=f'account-1'),
        InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
    ],
    [
        InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
    ],
    [
        InlineKeyboardButton("🆕 Create new gulag", callback_data=f'create-new'),
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)

async def abandon_game(game_id: int, user_id: int, query: CallbackQuery | None, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    p_status = r.get(user_id)

    if not p_status:
        return
    if p_status != 'SETTING' and p_status != 'DEPOSIT':
        return

    if game_id == 'nogame':
        if p_status == 'SETTING':
            await context.bot.send_message(chat_id=chat_id, text=REPLY_ABAN, parse_mode='HTML', reply_markup=reply_markup)
            r.delete(user_id)
        return

    #Only owner can abandon; status 9 == not paid
    sql = f"DELETE FROM games WHERE game_id='{game_id}' AND p1='{user_id}' AND status=9"

    mycursor.execute(sql)
    mydb.commit()

    if mycursor.rowcount < 1:
        r.delete(user_id)
        await query.answer('No game found')
        return

    await refound(game_id=game_id, user_id=user_id)

    # sql = f"DELETE FROM wallets WHERE game_id ='{game_id}' AND user_id='{user_id}'"

    # mycursor.execute(sql)
    # mydb.commit()

    await context.bot.send_message(chat_id=chat_id, text=REPLY_ABAN, parse_mode='HTML', reply_markup=reply_markup)
    r.delete(user_id)



async def stop_join(game_id: int, user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    p_status = r.get(user_id)

    if not p_status:
        return
    if p_status != 'JOINING' and p_status != 'DEPOSIT':
        return
    if game_id == 'nogame':
        if p_status == 'JOINING':
            await context.bot.send_message(chat_id=chat_id, text="<b>You are no longer joining a gulag!</b>\n\nIf you have deposited any tokens to the deposit address, you can withdraw them by clicking 'My Account'\n\n\n Don't worry you can still create new gulag or join to an existing gulag.", parse_mode='HTML', reply_markup=reply_markup)
            r.delete(user_id)
        return

    for i in range(2,6):
        sql = f"UPDATE games SET p{i}=NULL where game_id={game_id} AND status = 1 AND p{i}={user_id}"
        mycursor.execute(sql)

    mydb.commit()

    await refound(game_id=game_id, user_id=user_id)

    # sql = f"DELETE FROM wallets WHERE game_id ='{game_id}' AND user_id='{user_id}'"

    # mycursor.execute(sql)
    # mydb.commit()

    r.delete(user_id)
    await context.bot.send_message(chat_id=chat_id, text="<b>You are no longer joining a gulag!</b>\n\nIf you have deposited any tokens to the deposit address, you can withdraw them by clicking 'My Account'\n\n\n Don't worry you can still create new gulag or join to an existing gulag.", parse_mode='HTML', reply_markup=reply_markup)

async def cancel(game_id: int, user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    p_status = r.get(user_id)
    if p_status:
        return

    mydb.commit()
    p_num = 0
    for i in range(1,6):
        mycursor.execute(f"SELECT p{i} FROM games WHERE game_id={game_id} AND p{i}={user_id} AND status=1")
        myresults = mycursor.fetchall()
        if myresults:
            p_num = i
            break

    if p_num == 0:
        await context.bot.send_message(chat_id=chat_id, text=REPLY_GAME_END, reply_markup=reply_markup)
        return

    elif p_num == 1:
        mydb.commit()
        sql = f"SELECT p1,p2,p3,p4,p5 from games WHERE game_id={game_id} AND p1={user_id} AND status=1"
        mycursor.execute(sql)
        results = mycursor.fetchall()
        if not results:
            r.delete(user_id)
            return

        for i in range(0,5):
            if not results[0][i]:
                continue
            await refound(game_id=game_id, user_id=results[0][i])


        sql = f"UPDATE games SET status=4 WHERE game_id={game_id} AND p1={user_id}"
        mycursor.execute(sql)
        mydb.commit()
        if mycursor.rowcount < 1:
            r.delete(user_id)
            return

        r.delete(user_id)
        await context.bot.send_message(chat_id=chat_id, text=f"<b>You have ceased the gulag #{game_id}!</b>\n\nIf you have deposited any tokens to the deposit address, you can withdraw them by clicking 'My Account'\n\n\n Don't worry you can still create new gulag or join to an existing gulag.", parse_mode='HTML', reply_markup=reply_markup)
        await send_group_msg(context=context,msg_type=MsgType.CANCEL, game_id=game_id, user_id=user_id)
    else:
        await refound(game_id=game_id, user_id=user_id)

        sql = f"UPDATE games SET p{p_num}=NULL where game_id={game_id} AND status = 1 AND p{i}={user_id}"
        mycursor.execute(sql)
        mydb.commit()
        if mycursor.rowcount < 1:
            r.delete(user_id)
            return

        r.delete(user_id)
        await context.bot.send_message(chat_id=chat_id, text=f"<b>You are no longer in the gulag #{game_id}!</b>\n\nIf you have deposited any tokens to the deposit address, you can withdraw them by clicking 'My Account'\n\n\n Don't worry you can still create new gulag or join to an existing gulag.", parse_mode='HTML', reply_markup=reply_markup)


async def refound(user_id: int, game_id:int) -> bool:
    client = Client("https://api.mainnet-beta.solana.com")
    mydb.commit()
    mycursor.execute(f"SELECT pub_key, priv_key FROM wallets WHERE user_id={user_id} AND game_id={game_id}")
    myresults = mycursor.fetchall()

    if not myresults:
        return False


    sender_priv_key = hex_to_base58(myresults[0][1])
    sender = Keypair.from_seed(base58.b58decode(sender_priv_key))
    sender_pub_key = sender.pubkey()

    sender_token_account = get_associated_token_address(sender_pub_key, bombo_mint_address)

    mycursor.execute(f"SELECT pub_key FROM accounts WHERE user_id={user_id}")
    myresults = mycursor.fetchall()
    public_key = 0

    if not myresults:
        keypair = Keypair()
        public_key = keypair.pubkey()
        private_key = keypair.secret()

        sql = "INSERT INTO accounts(user_id, pub_key,priv_key) VALUES (%s,%s,%s)"
        val = (user_id, f'{public_key}', f'{private_key.hex()}')
        mycursor.execute(sql, val)
    else:
        public_key = Pubkey.from_string(myresults[0][0])
    print(f"recipient: {public_key}")
    recipient_token_account = get_associated_token_address(public_key, bombo_mint_address)

    token_accounts = client.get_token_accounts_by_owner(sender_pub_key, TokenAccountOpts(mint=bombo_mint_address))
    if not token_accounts.value:
        token_balance = 0
    else:
        token_balance = client.get_token_account_balance(token_accounts.value[0].pubkey).value.amount
        if not token_balance:
            token_balance = 0

    token_balance = int(token_balance)

    if token_balance <= 0:
        r.delete(user_id)
        return

    try:
        transaction = Transaction().add(
        transfer(
            TransferParams(
                program_id=TOKEN_PROGRAM_ID,
                source=sender_token_account,
                dest=recipient_token_account,
                owner=sender_pub_key,
                amount=token_balance
            )
        )
        )
        response = client.send_transaction(transaction, sender)
        print(f"Transaction Signature: {response}")
    except:
        pass

    return True

def hex_to_base58(hex_string):
    bytes_str = bytes.fromhex(hex_string)
    base58_str = base58.b58encode(bytes_str)
    return base58_str.decode("UTF-8")

async def withdraw(address: str, user_id: int) -> bool:
    client = Client("https://api.mainnet-beta.solana.com")
    mydb.commit()
    mycursor.execute(f"SELECT pub_key, priv_key FROM accounts WHERE user_id={user_id}")
    myresults = mycursor.fetchall()

    if not myresults:
        return False


    sender_priv_key = hex_to_base58(myresults[0][1])
    sender = Keypair.from_seed(base58.b58decode(sender_priv_key))
    sender_pub_key = sender.pubkey()

    sender_token_account = get_associated_token_address(sender_pub_key, bombo_mint_address)

    try:
        recipient_token_account = get_associated_token_address(address, bombo_mint_address)
    except:
        return False

    token_accounts = client.get_token_accounts_by_owner(sender_pub_key, TokenAccountOpts(mint=bombo_mint_address))
    if not token_accounts.value:
        token_balance = 0
    else:
        token_balance = client.get_token_account_balance(token_accounts.value[0].pubkey).value.amount
        if not token_balance:
            token_balance = 0

    token_balance = int(token_balance)

    if token_balance <= 0:
        r.delete(user_id)
        return

    try:
        transaction = Transaction().add(
            transfer(
                TransferParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=sender_token_account,
                    dest=recipient_token_account,
                    owner=sender_pub_key,
                    amount=token_balance
                )
            )
        )
        response = client.send_transaction(transaction, sender)

        print(f"Transaction Signature: {response}")
        return True
    except:
        return False
