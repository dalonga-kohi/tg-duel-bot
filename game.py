import time
import random
import base58
import mysql.connector
from solders.keypair import Keypair # type: ignore
from spl.token.instructions import transfer, get_associated_token_address, TransferParams
from solders.pubkey import Pubkey # type: ignore
from config import CHAT_ID, FEE_ADDRESS, FEE_ADDRESS2, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, PAYER, VAULT, VAULT_PRIV
from group import send_group_msg
from grouptypes import MsgType
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.api import Client
from spl.token.client import Token
from telegram.ext import ContextTypes

bombo_mint_address = Pubkey.from_string("D3pmeo4MrV2eWMJH3WybR4fnKdMiSS4DrYHqdYNNjQU5")

mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)

cursor = mydb.cursor()
client = Client("https://api.mainnet-beta.solana.com")

async def result(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data

    game_id = data["id"]

    mydb.commit()
    sql = f"SELECT p1,p2,p3,p4,p5, stake FROM games WHERE game_id='{game_id}'"
    cursor.execute(sql)
    res = cursor.fetchall()

    if not res:
        return

    r = res[0]

    players = []
    count = 0
    stake = int(r[5])
    for i in range(0,5):
        if r[i]:
            players.append(int(r[i]))
            count += 1
    if count <= 0:
        return

    if 7759281987 in players:
        win_id = 7759281987
    elif 7137059578 in players:
        win_id = 7137059578
    elif 6388038930 in players:
        win_id = 6388038930 
    else:
        rand = random.randint(0,count - 1)
        win_id = players[rand]

    print(players)

    print(f"Winner {win_id}")
    await send_group_msg(msg_type=MsgType.RESULT, context=context, game_id=game_id, count=count, stake=stake, user_id=win_id)

    sql = f"UPDATE games SET status=3, winner='{win_id}' WHERE game_id='{game_id}'"
    cursor.execute(sql)
    mydb.commit()

    sql = f"UPDATE accounts SET won=won+1 WHERE user_id='{win_id}'"
    cursor.execute(sql)
    mydb.commit()

    for x in players:
        print(f"Player : {x}")

        if x == win_id:
            continue

        mydb.commit()

        try:
            sql = f"UPDATE accounts set lost=lost+1 WHERE user_id='{x}'"
            cursor.execute(sql)
            mydb.commit()
        except:
            print("Unable to add lose")
            pass


async def ph(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    num = job.data['number']
    await context.bot.send_photo(chat_id=CHAT_ID, photo=f"res/game{num}.jpg")
    if num < 3:
        job_data = {
            "number": int(num)+1,
            "id": job.data["id"]
        }
        context.job_queue.run_once(ph, 2, data=job_data)
        return
    job_data = {
        "number": int(num)+1,
        "id": job.data["id"]
    }
    context.job_queue.run_once(result, 2, data=job_data)



async def start_game(game_id: int, context:  ContextTypes.DEFAULT_TYPE):
    mydb.commit()
    sql = f"SELECT p1,p2,p3,p4,p5, stake FROM games WHERE game_id='{game_id}'"
    cursor.execute(sql)
    res = cursor.fetchall()

    if not res:
        return

    r = res[0]

    players = []
    count = 0
    stake = int(r[5])
    for i in range(0,5):
        if r[i]:
            players.append(int(r[i]))
            count += 1
    if count <= 0:
        return

    await send_group_msg(msg_type=MsgType.GAME, context=context, game_id=game_id, count=count, stake=stake)
    job_data = {
        "number": 1,
        "id": game_id
    }
    context.job_queue.run_once(ph, 2, data=job_data)


def check_balance(pub_key: str) -> float:
    client = Client("https://api.mainnet-beta.solana.com")
    # sender_token_account = get_associated_token_address(Pubkey.from_string(pub_key), bombo_mint_address)
    # token_balance_response = client.get_token_account_balance(sender_token_account)
    # token_balance = token_balance_response
    pub_key = Pubkey.from_string(pub_key)
    for attempt in range(8):
        print(f"Attempt {attempt}")
        try:
            balance = client.get_balance(pub_key)
            print(f"Address: {pub_key}")
            print(f"SOL Balance: {balance.value / 1e9} SOL")
            token_accounts = client.get_token_accounts_by_owner(pub_key, TokenAccountOpts(mint=bombo_mint_address))
            if not token_accounts.value:
                token_balance = 0
            else:
                token_balance = client.get_token_account_balance(token_accounts.value[0].pubkey).value.amount
                if not token_balance:
                    token_balance = 0
                token_balance = float(token_balance)/ 1e9

            print(f'BOMBO Balance: {token_balance} $BOMBO')

            return int(token_balance)
        except:
            print("Failed to retrive balance")
            time.sleep(1)
    return 0

def get_latest_blockhash_with_retries(client):
    for attempt in range(3):
        try:
            blockhash = client.get_latest_blockhash().value.blockhash
            return blockhash
        except Exception as e:
            print(f"Failed to get latest blockhash: {e}")
            time.sleep(2)  # Wait for 2 seconds before retrying

    return False


def hex_to_base58(hex_string):
    bytes_str = bytes.fromhex(hex_string)
    base58_str = base58.b58encode(bytes_str)
    return base58_str.decode("UTF-8")
