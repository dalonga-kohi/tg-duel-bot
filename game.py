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

    rand = random.randint(0,count - 1)
    win_id = players[rand]
    print(players)

    print(f"Winner {win_id}")

    await send_group_msg(msg_type=MsgType.GAME, context=context, game_id=game_id, count=count, stake=stake)
    time.sleep(3)

    await context.bot.send_photo(chat_id=CHAT_ID, photo="res/game1.jpg")
    time.sleep(3)
    await context.bot.send_photo(chat_id=CHAT_ID, photo="res/game2.jpg")
    time.sleep(3)
    await context.bot.send_photo(chat_id=CHAT_ID, photo="res/game3.jpg")
    time.sleep(3)

    await send_group_msg(msg_type=MsgType.RESULT, context=context, game_id=game_id, count=count, stake=stake, user_id=win_id)

    sql = f"UPDATE games SET status=3, winner='{win_id}' WHERE game_id='{game_id}'"
    cursor.execute(sql)
    mydb.commit()

    sql = f"SELECT pub_key, priv_key, won, lost, total, withdraw FROM accounts WHERE user_id='{win_id}'"
    cursor.execute(sql)
    res = cursor.fetchall()
    pot = stake*count*0.985

    if not res:
        keypair = Keypair()
        public_key = keypair.pubkey()
        private_key = keypair.secret()

        sql = "INSERT INTO accounts(user_id, pub_key,priv_key, won, total) VALUES (%s,%s,%s, %s, %s)"
        val = (win_id, f'{public_key}', f'{private_key.hex()}', 1, pot)
        cursor.execute(sql, val)
        mydb.commit()
    else:

        won = res[0][2]
        lost = res[0][3]
        total = res[0][4]
        wd = pot + float(res[0][5])
        sql = f"UPDATE accounts SET won={won+1},total={total+pot},withdraw={wd} WHERE user_id='{win_id}'"
        cursor.execute(sql)
        mydb.commit()

    cursor.execute("SELECT priv_key FROM config WHERE name='payer'")
    p_priv = cursor.fetchall()

    if not p_priv:
        payer = Keypair.from_seed(base58.b58decode(hex_to_base58(PAYER)))
    else:
        payer = Keypair.from_seed(base58.b58decode(hex_to_base58(p_priv[0][0])))

    token = Token(client, bombo_mint_address, TOKEN_PROGRAM_ID, payer)
    print("TRYING")
    cursor.execute("SELECT priv_key FROM config WHERE name='vault'")
    p_priv = cursor.fetchall()

    if not p_priv:
        recipient = Keypair.from_seed(base58.b58decode(hex_to_base58(VAULT_PRIV)))
    else:
        recipient = Keypair.from_seed(base58.b58decode(hex_to_base58(p_priv[0][0])))


    try:
        recipient_token_account = get_associated_token_address(recipient.pubkey(), bombo_mint_address)
    except Exception as ex:
        print(ex)
        try:
            recipient_token_account = token.create_associated_token_account(owner=recipient.pubkey(), skip_confirmation=False, recent_blockhash=None)
        except Exception as ex:
            print(ex)
            print('No funds')
    fee = 0

    for x in players:
        print(f"Player : {x}")
        mydb.commit()
        sql = f"SELECT pub_key, priv_key FROM wallets WHERE user_id='{x}' AND game_id='{game_id}'"
        cursor.execute(sql)
        res = cursor.fetchall()
        print(f"CONN")
        if not res:
            continue

        priv = hex_to_base58(res[0][1])
        sender = Keypair.from_seed(base58.b58decode(priv))
        print(f"KEYS")

        try:
            sender_token_account = get_associated_token_address(sender.pubkey(),bombo_mint_address)
        except:
            try:
                sender_token_account = token.create_associated_token_account(owner=sender.pubkey(), skip_confirmation=False, recent_blockhash=None)
            except:
                print('No funds for creation')

        print("SENDER")
        try:
            amount = token.get_balance(sender_token_account).value.amount
        except:
            amount = 0

        token_balance = float(amount) /1e9
        print(f"Balance: {token_balance}")

        time.sleep(10)
        if token_balance > 0:
            for a in range(10):
                try:
                    block = get_latest_blockhash_with_retries(client)
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

                    fee += int(float(token_balance)*1000000000)
                    break
                except Exception as ex:
                    print(ex)
                    print('Transit retry')
                    time.sleep(3)



        if x == win_id:
            continue

        sql = f"SELECT lost from accounts WHERE user_id='{x}'"
        cursor.execute(sql)
        res = cursor.fetchall()

        try:
            if not res:
                tmp = Keypair()
                sql = "INSERT INTO accounts(user_id, pub_key,priv_key, lost) VALUES (%s,%s,%s, %s)"
                val = (x, f'{tmp.pubkey()}', f'{tmp.secret.hex()}', 1)
                cursor.execute(sql, val)
                mydb.commit()
            else:
                print(f"Lost: {res[0][0]+1}")
                sql = f"UPDATE accounts set lost={res[0][0] + 1} WHERE user_id='{x}'"
                cursor.execute(sql)
                mydb.commit()
        except:
            pass

    sender_token_account = recipient_token_account
    cursor.execute("SELECT pub_key, val FROM config WHERE name='fee1'")
    fee_add = cursor.fetchall()

    if not fee_add:
        fee_pub = FEE_ADDRESS
        per = 0.0125
    else:
        per = float(fee_add[0][1])
        fee_pub = fee_add[0][0]
    try:
        try:
            recipient_token_account = get_associated_token_address(Pubkey.from_string(fee_pub), bombo_mint_address)
        except:
            recipient_token_account = token.create_associated_token_account(owner=Pubkey.from_string(fee_pub), skip_confirmation=False, recent_blockhash=None)
    except:
        print('No Funds for creation')

    time.sleep(10)

    for a in range(5):
        try:
            block = get_latest_blockhash_with_retries(client)
            print(f'Fee: {int(fee*per)}')
            transaction = Transaction()
            instruction = transfer(
                TransferParams(
                amount=int(fee*per),
                dest=recipient_token_account,
                owner=recipient.pubkey(),
                source=sender_token_account,
                program_id=TOKEN_PROGRAM_ID,
                )
            )
            transaction.add(instruction)
            transaction.fee_payer = payer.pubkey()
            transaction.recent_blockhash = block
            transaction.sign_partial(payer)
            transaction.sign_partial(recipient)
            print('HERE')
            signature = client.send_transaction(transaction,recipient,payer, recent_blockhash=block)

            print(f"Transaction Signature: {signature}")
            break
        except Exception as ex:
            print(ex)
            print('NO FEE')
            time.sleep(2)


    cursor.execute("SELECT pub_key, val FROM config WHERE name='fee2'")
    fee_add = cursor.fetchall()

    if not fee_add:
        fee_pub = FEE_ADDRESS
        per = 0.0025
    else:
        per = float(fee_add[0][1])
        fee_pub = fee_add[0][0]
    try:
        try:
            recipient_token_account = get_associated_token_address(Pubkey.from_string(fee_pub), bombo_mint_address)
        except:
            recipient_token_account = token.create_associated_token_account(owner=Pubkey.from_string(fee_pub), skip_confirmation=False, recent_blockhash=None)
    except:
        print('No Funds for creation')

    time.sleep(8)
    for a in range(5):
        try:
            block = get_latest_blockhash_with_retries(client)
            print(f'Fee: {int(fee*per)}')
            transaction = Transaction()
            instruction = transfer(
                TransferParams(
                amount=int(fee*per),
                dest=recipient_token_account,
                owner=recipient.pubkey(),
                source=sender_token_account,
                program_id=TOKEN_PROGRAM_ID,
                )
            )
            transaction.add(instruction)
            transaction.fee_payer = payer.pubkey()
            transaction.recent_blockhash = block
            transaction.sign_partial(payer)
            transaction.sign_partial(recipient)
            print('HERE')
            signature = client.send_transaction(transaction,recipient,payer, recent_blockhash=block)

            print(f"Transaction Signature: {signature}")
            break
        except Exception as ex:
            print(ex)
            print('NO FEE')
            time.sleep(2)


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