import time
import mysql.connector
import redis
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, PAYER, R_HOST, R_PORT, REPLY_ABAN, REPLY_GAME_END, VAULT_PRIV
from solders.pubkey import Pubkey # type: ignore
from spl.token.instructions import transfer, get_associated_token_address, TransferParams
from solders.keypair import Keypair # type: ignore
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.client import Token
import base58
from solana.rpc.types import TxOpts
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
    print(p_status)
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

    print("Refound")
    try:
        await context.bot.send_message(chat_id=chat_id, text='Looking for your account details... 🔍')
        await refound(game_id=game_id, user_id=user_id)
    except:
        pass

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
    print("STOP JOINING")
    try:
        await context.bot.send_message(chat_id=chat_id, text='Looking for your account details... 🔍')

        await refound(game_id=game_id, user_id=user_id)
    except:
        pass

    sql = f"DELETE FROM wallets WHERE game_id ='{game_id}' AND user_id='{user_id}'"

    mycursor.execute(sql)
    mydb.commit()

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
            try:
                await context.bot.send_message(chat_id=results[0][i], text='Looking for your account details... 🔍')
                await refound(game_id=game_id, user_id=results[0][i])
            except:
                pass


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
        try:
            await context.bot.send_message(chat_id=chat_id, text='Looking for your account details... 🔍')
            await refound(game_id=game_id, user_id=user_id)
        except:
            pass

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
    print("Fetching...")
    if not myresults:
        return False
    print("Fetched")
    sender_priv_key = hex_to_base58(myresults[0][1])
    sender = Keypair.from_seed(base58.b58decode(sender_priv_key))
    sender_pub_key = sender.pubkey()

    payer = Keypair.from_seed(base58.b58decode(hex_to_base58(PAYER)))
    token = Token(client, bombo_mint_address, TOKEN_PROGRAM_ID, payer)
    print(f"Payer: {payer.pubkey()}")
    print("Initialized")

    try:
        sender_token_account = get_associated_token_address(sender.pubkey(), mint=bombo_mint_address)
    except Exception as ex:
        print(ex)
        sender_token_account = token.create_associated_token_account(owner=sender.pubkey(), skip_confirmation=False, recent_blockhash=None)
    print("SENDER")
    mycursor.execute(f"SELECT pub_key FROM accounts WHERE user_id={user_id}")
    myresults = mycursor.fetchall()
    public_key = 0

    print("Fetching 2...")

    if not myresults:
        keypair = Keypair()
        public_key = keypair.pubkey()
        private_key = keypair.secret()

        sql = "INSERT INTO accounts(user_id, pub_key,priv_key) VALUES (%s,%s,%s)"
        val = (user_id, f'{public_key}', f'{private_key.hex()}')
        mycursor.execute(sql, val)
    else:
        public_key = Pubkey.from_string(myresults[0][0])

    print("KEYS obtained")
    try:
        recipient_token_account = get_associated_token_address(public_key, bombo_mint_address)
    except Exception as ex:
        print(ex)
        recipient_token_account = token.create_associated_token_account(owner=public_key, skip_confirmation=False, recent_blockhash=None)

    for a in range(5):
        try:
            amount = token.get_balance(sender_token_account).value.amount
        except:
            time.sleep(2)
            continue

        if amount == 0:
            time.sleep(2)
            continue
        else:
            break

    token_balance = float(amount) /1e9

    if token_balance <= 0:
        print('No balance')
        r.delete(user_id)
        return

    print(f"Amount: {token_balance}")
    print(f"Pub: {sender_pub_key}")
    print(f"Sender: {sender_token_account}")

    print(f"Priv: {sender.secret().hex()}")
    print(f"Recip: {public_key}")
    print(f"Recip token: {recipient_token_account}")

    block = get_latest_blockhash_with_retries(client)
    if not block:
        return False

    try:
        transaction = Transaction()
        instruction = transfer(
            TransferParams(
            amount=int(float(token_balance)*1000000000),
            dest=recipient_token_account,
            owner=sender.pubkey(),
            source=sender_token_account,
            program_id=TOKEN_PROGRAM_ID,
            )
        )
        transaction.add(instruction)
        transaction.fee_payer = payer.pubkey()
        transaction.recent_blockhash = block
        transaction.sign_partial(payer)
        transaction.sign_partial(sender)

        signature = client.send_transaction(transaction,sender,payer, recent_blockhash=block)

        print(f"Transaction Signature: {signature}")

        return True
    except:
        return False

def hex_to_base58(hex_string):
    bytes_str = bytes.fromhex(hex_string)
    base58_str = base58.b58encode(bytes_str)
    return base58_str.decode("UTF-8")

async def withdraw(address: str, user_id: int) -> str:
    client = Client("https://api.mainnet-beta.solana.com")
    mydb.commit()
    mycursor.execute(f"SELECT pub_key, priv_key FROM accounts WHERE user_id={user_id}")
    myresults = mycursor.fetchall()

    if not myresults:
        print('No ACCOUNT')
        return None

    sender_priv_key = hex_to_base58(myresults[0][1])
    sender = Keypair.from_seed(base58.b58decode(sender_priv_key))
    sender_pub_key = sender.pubkey()

    try:
        public_key = Pubkey.from_string(address)
    except:
        return None

    payer = Keypair.from_seed(base58.b58decode(hex_to_base58(PAYER)))
    token = Token(client, bombo_mint_address, TOKEN_PROGRAM_ID, payer)


    try:
        try:
            sender_token_account = token.get_accounts_by_owner(owner=sender_pub_key, commitment=None, encoding='base64').value[0].pubkey
        except:
            sender_token_account = token.create_associated_token_account(owner=sender_pub_key, skip_confirmation=False, recent_blockhash=None)
        try:
            recipient_token_account = token.get_accounts_by_owner(owner=Pubkey.from_string(address), commitment=None, encoding='base64').value[0].pubkey
        except:
            try:
                recipient_token_account = token.create_associated_token_account(owner=public_key, skip_confirmation=False, recent_blockhash=None)
            except:
                return None
    except:
        print('No Funds')
        return None

    try:
        amount = token.get_balance(sender_token_account).value.amount
    except:
        amount = 0


    token_balance = float(amount) /1e9

    if token_balance <= 0:
        return None

    print(f"Amount: {token_balance}")
    print(f"Pub: {sender_pub_key}")
    print(f"Sender: {sender_token_account}")

    print(f"Priv: {sender.secret().hex()}")
    print(f"Recip: {public_key}")
    print(f"Recip token: {recipient_token_account}")

    block = get_latest_blockhash_with_retries(client)
    if not block:
        print('No block')
        return None

    print('Attempt')
    try:
        transaction = Transaction()
        instruction = transfer(
            TransferParams(
            amount=int(float(token_balance)*1000000000),
            dest=recipient_token_account,
            owner=sender.pubkey(),
            source=sender_token_account,
            program_id=TOKEN_PROGRAM_ID,
            )
        )
        transaction.add(instruction)
        transaction.fee_payer = payer.pubkey()
        transaction.recent_blockhash = block
        transaction.sign_partial(payer)
        transaction.sign_partial(sender)

        signature = client.send_transaction(transaction,sender,payer, recent_blockhash=block)

        print(f"Transaction Signature: {signature}")

        return f"{signature.value}"
    except Exception as ex:
        print(ex)
        return False

def get_latest_blockhash_with_retries(client):
    for attempt in range(8):
        try:
            blockhash = client.get_latest_blockhash().value.blockhash
            return blockhash
        except Exception as e:
            print(f"Failed to get latest blockhash: {e}")
            time.sleep(1)  # Wait for 2 seconds before retrying

    return False


async def wd_total(address: str, user_id: int) -> str:
    client = Client("https://api.mainnet-beta.solana.com")
    mydb.commit()
    mycursor.execute(f"SELECT priv_key FROM config WHERE name='vault'")
    myresults = mycursor.fetchall()

    if not myresults:
        print('No ACCOUNT')
        return None

    sender_priv_key = hex_to_base58(myresults[0][0])
    sender = Keypair.from_seed(base58.b58decode(sender_priv_key))
    sender_pub_key = sender.pubkey()
    print(f"Pub: {sender_pub_key}")
    try:
        public_key = Pubkey.from_string(address)
    except:
        return None

    payer = Keypair.from_seed(base58.b58decode(hex_to_base58(PAYER)))
    token = Token(client, bombo_mint_address, TOKEN_PROGRAM_ID, payer)


    try:
        try:
            sender_token_account = token.get_accounts_by_owner(owner=sender_pub_key, commitment=None, encoding='base64').value[0].pubkey
        except:
            sender_token_account = token.create_associated_token_account(owner=sender_pub_key, skip_confirmation=False, recent_blockhash=None)
        try:
            recipient_token_account = token.get_accounts_by_owner(owner=Pubkey.from_string(address), commitment=None, encoding='base64').value[0].pubkey
        except:
            try:
                recipient_token_account = token.create_associated_token_account(owner=public_key, skip_confirmation=False, recent_blockhash=None)
            except:
                return None
    except:
        print('No Funds')
        return None

    mycursor.execute(f"SELECT withdraw FROM accounts WHERE user_id='{user_id}'")
    myresults = mycursor.fetchall()

    if not myresults:
        print('No ACCOUNT')
        return None

    token_balance = myresults[0][0]
    # token_balance = float(amount) /1e9

    if token_balance <= 0:
        return None

    print(f"Amount: {token_balance}")
    print(f"Pub: {sender_pub_key}")
    print(f"Sender: {sender_token_account}")

    print(f"Priv: {sender.secret().hex()}")
    print(f"Recip: {public_key}")
    print(f"Recip token: {recipient_token_account}")

    block = get_latest_blockhash_with_retries(client)
    if not block:
        print('No block')
        return None

    print('Attempt')
    try:
        transaction = Transaction()
        instruction = transfer(
            TransferParams(
            amount=int(float(token_balance)*1000000000),
            dest=recipient_token_account,
            owner=sender.pubkey(),
            source=sender_token_account,
            program_id=TOKEN_PROGRAM_ID,
            )
        )
        transaction.add(instruction)
        transaction.fee_payer = payer.pubkey()
        transaction.recent_blockhash = block
        transaction.sign_partial(payer)
        transaction.sign_partial(sender)

        signature = client.send_transaction(transaction,sender,payer, recent_blockhash=block)

        print(f"Transaction Signature: {signature}")
        mycursor.execute(f"UPDATE accounts SET withdraw=0 WHERE user_id='{user_id}'")
        mydb.commit()

        return f"{signature.value}"
    except Exception as ex:
        print(ex)
        return False