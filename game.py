from datetime import time
import random
import base58
import mysql.connector
from solders.keypair import Keypair # type: ignore
from spl.token.instructions import transfer, get_associated_token_address, TransferParams
from solders.pubkey import Pubkey # type: ignore
from config import FEE_ADDRESS, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER
from group import send_group_msg
from grouptypes import MsgType
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.api import Client

bombo_mint_address = Pubkey.from_string("D3pmeo4MrV2eWMJH3WybR4fnKdMiSS4DrYHqdYNNjQU5")

mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)

cursor = mydb.cursor()
client = Client("https://api.mainnet-beta.solana.com")

async def start_game(game_id: int, context):
    mydb.commit()
    sql = f"SELECT p1,p2,p3,p4,p5, stake FROM games WHERE game_id='{game_id}' AND status=1"
    cursor.execute(sql)
    r = cursor.fetchall()

    if not r:
        return

    players = []
    count = 0
    stake = r[5]
    for i in range(0,5):
        if r[i]:
            players.append(int(r[i]))
            count += 1
    if count <= 0:
        return

    rand = random.randint(0,count - 1)
    win_id = players[rand]

    await send_group_msg(msg_type=MsgType.GAME, context=context, game_id=game_id, count=count, stake=stake)
    await time.sleep(3)
    await send_group_msg(msg_type=MsgType.RESULT, context=context, game_id=game_id, count=count, stake=stake, user_id=win_id)

    sql = f"UPDATE games SET status=3, winner='{win_id}' WHERE game_id='{game_id}'"
    cursor.execute(sql)
    mydb.commit()

    sql = f"UPDATE accounts SET status=3, winner='{win_id}' WHERE user_id='{win_id}'"
    cursor.execute(sql)
    mydb.commit()

    sql = f"SELECT pub_key, priv_key, won, lost, total FROM accounts WHERE user_id='{win_id}'"
    cursor.execute(sql)
    res = cursor.fetchall()
    pot = stake*count*0.99
    if not res:
        keypair = Keypair()
        public_key = keypair.pubkey()
        private_key = keypair.secret()
        recipient = keypair

        sql = "INSERT INTO accounts(user_id, pub_key,priv_key, won, total) VALUES (%s,%s,%s, %s, %s)"
        val = (win_id, f'{public_key}', f'{private_key.hex()}', 1, pot)
        cursor.execute(sql, val)
    else:
        private_key = hex_to_base58(res[0][1])
        recipient = Keypair.from_seed(base58.b58decode(private_key))
        public_key = recipient.pubkey
        won = res[0][2]
        lost = res[0][3]
        total = res[0][4]
        sql = f"UPDATE accounts SET won={won+1},total={total+pot} WHERE user_id='{win_id}'"
        cursor.execute(sql)
        mydb.commit()

    recipient_token_account = get_associated_token_address(public_key, bombo_mint_address)
    fee = 0
    for x in players:
        sql = f"SELECT pub_key, priv_key FROM wallets WHERE user_id='{x}' AND game_id='{game_id}'"
        cursor.execute(sql)
        res = cursor.fetchall()

        if not res:
            continue

        priv = hex_to_base58(res[0][1])
        sender = Keypair.from_seed(base58.b58decode(priv))

        sender_token_account = get_associated_token_address(sender.pubkey, bombo_mint_address)
        token_accounts = client.get_token_accounts_by_owner(sender.pubkey, TokenAccountOpts(mint=bombo_mint_address))
        if not token_accounts.value:
            token_balance = 0
        else:
            token_balance = client.get_token_account_balance(token_accounts.value[0].pubkey).value.amount
            if not token_balance:
                token_balance = 0

        token_balance = int(token_balance)

        if token_balance <= 0:
            continue


        try:
            transaction = Transaction().add(
            transfer(
                TransferParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=sender_token_account,
                    dest=recipient_token_account,
                    owner=sender.pubkey,
                    amount=token_balance
                )
            )
            )
            response = client.send_transaction(transaction, sender)
            print(f"Transaction Signature: {response}")
            fee += token_balance
        except:
            continue

    try:
        recipient_token_account = get_associated_token_address(Pubkey.from_string(FEE_ADDRESS), bombo_mint_address)
        sender_token_account = get_associated_token_address(recipient.pubkey, bombo_mint_address)
        transaction = Transaction().add(
                transfer(
                    TransferParams(
                        program_id=TOKEN_PROGRAM_ID,
                        source=sender_token_account,
                        dest=recipient_token_account,
                        owner=sender.pubkey,
                        amount=fee*0.01
                    )
                )
        )
        response = client.send_transaction(transaction, sender)
        print(f"Transaction Signature: {response}")
    except:
        print('No Fee')







def hex_to_base58(hex_string):
    bytes_str = bytes.fromhex(hex_string)
    base58_str = base58.b58encode(bytes_str)
    return base58_str.decode("UTF-8")