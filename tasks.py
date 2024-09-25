import time
import base58
import schedule
from schedule import every, repeat
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.api import Client
from spl.token.client import Token
import mysql.connector
from solders.keypair import Keypair # type: ignore
from spl.token.instructions import transfer, get_associated_token_address, TransferParams
from solders.pubkey import Pubkey # type: ignore
from config import DECIMALS, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, PAYER, VAULT_PRIV, MINT, FEE_VAL

bombo_mint_address = Pubkey.from_string(MINT)


client = Client("https://api.mainnet-beta.solana.com")

def hex_to_base58(hex_string):
    bytes_str = bytes.fromhex(hex_string)
    base58_str = base58.b58encode(bytes_str)
    return base58_str.decode("UTF-8")

@repeat(every(1).minute)
def vault():
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )

    cursor = mydb.cursor()
    mydb.commit()
    cursor.execute("SELECT pub_key, priv_key, games.game_id, status, user_id FROM wallets JOIN games ON games.game_id=wallets.game_id WHERE wallets.date > ADDDATE(NOW(), INTERVAL -3 DAY) AND (status=3 OR status=4)")
    res = cursor.fetchall()

    cursor.execute("SELECT priv_key FROM config WHERE name='payer'")
    p_priv = cursor.fetchall()

    if not p_priv:
        payer = Keypair.from_seed(base58.b58decode(hex_to_base58(PAYER)))
    else:
        payer = Keypair.from_seed(base58.b58decode(hex_to_base58(p_priv[0][0])))


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

    token = Token(client, bombo_mint_address, TOKEN_PROGRAM_ID, payer)

    for row in res:
        priv = hex_to_base58(row[1])
        sender = Keypair.from_seed(base58.b58decode(priv))

#        print(sender.pubkey())

        try:
            sender_token_account = get_associated_token_address(sender.pubkey(),bombo_mint_address)
        except:
            try:
                sender_token_account = token.create_associated_token_account(owner=sender.pubkey(), skip_confirmation=False, recent_blockhash=None)
            except:
                print('No funds for creation')

        try:
            amount = token.get_balance(sender_token_account).value.amount
        except:
            amount = 0

        token_balance = float(amount) /(10**DECIMALS)
#        print(f"Balance: {token_balance}")
        if token_balance <= 0:
            continue

        try:
            block = client.get_latest_blockhash().value.blockhash
 #           print(block)
            transaction = Transaction()
            instruction = transfer(
                TransferParams(
                amount=int(float(token_balance)*(10**DECIMALS)),
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

            if int(row[3]) == 3:
                cursor.execute(f"SELECT winner FROM games WHERE game_id={row[2]}")
                win = cursor.fetchall()
                win_id = win[0][0]
                cursor.execute(f'UPDATE accounts SET total=total+{token_balance*FEE_VAL}, withdraw=withdraw+{token_balance*FEE_VAL} WHERE user_id="{win_id}"')
                mydb.commit()
            else:
                cursor.execute(f'UPDATE accounts SET withdraw=withdraw+{token_balance*FEE_VAL} WHERE user_id="{row[4]}"')
                mydb.commit()
            cursor.close()
            mydb.close()


  #          time.sleep(2)
            # cursor.execute("SELECT pub_key, val FROM config WHERE name='fee1'")
            # fee_add = cursor.fetchall()
            # if not fee_add:
            #     fee_pub = FEE_ADDRESS
            #     per = 0.0125
            # else:
            #     per = float(fee_add[0][1])
            #     fee_pub = fee_add[0][0]
            # try:
            #     try:
            #         fee_token_account = get_associated_token_address(Pubkey.from_string(fee_pub), bombo_mint_address)
            #     except:
            #         fee_token_account = token.create_associated_token_account(owner=Pubkey.from_string(fee_pub), skip_confirmation=False, recent_blockhash=None)
            # except:
            #     print('No Funds for creation')

            # block = client.get_latest_blockhash().value.blockhash

            # print(f'Fee: {int(token_balance*per*1000000000)}')
            # transaction = Transaction()
            # instruction = transfer(
            #     TransferParams(
            #     amount=int(token_balance*per*1000000000),
            #     dest=fee_token_account,
            #     owner=recipient.pubkey(),
            #     source=recipient_token_account,
            #     program_id=TOKEN_PROGRAM_ID,
            #     )
            # )
            # transaction.add(instruction)
            # transaction.fee_payer = payer.pubkey()
            # transaction.recent_blockhash = block
            # transaction.sign_partial(payer)
            # transaction.sign_partial(recipient)
            # print('HERE')
            # signature = client.send_transaction(transaction,recipient,payer, recent_blockhash=block)

            # print(f"Transaction Signature: {signature}")

            # block = client.get_latest_blockhash().value.blockhash
            # cursor.execute("SELECT pub_key, val FROM config WHERE name='fee2'")
            # fee_add = cursor.fetchall()
            # if not fee_add:
            #     fee_pub = FEE_ADDRESS
            #     per = 0.0025
            # else:
            #     per = float(fee_add[0][1])
            #     fee_pub = fee_add[0][0]
            # try:
            #     try:
            #         fee_token_account = get_associated_token_address(Pubkey.from_string(fee_pub), bombo_mint_address)
            #     except:
            #         fee_token_account = token.create_associated_token_account(owner=Pubkey.from_string(fee_pub), skip_confirmation=False, recent_blockhash=None)
            # except:
            #     print('No Funds for creation')

            # block = client.get_latest_blockhash().value.blockhash

            # print(f'Fee: {int(token_balance*per*1000000000)}')
            # transaction = Transaction()
            # instruction = transfer(
            #     TransferParams(
            #     amount=int(token_balance*per*1000000000),
            #     dest=fee_token_account,
            #     owner=recipient.pubkey(),
            #     source=recipient_token_account,
            #     program_id=TOKEN_PROGRAM_ID,
            #     )
            # )
            # transaction.add(instruction)
            # transaction.fee_payer = payer.pubkey()
            # transaction.recent_blockhash = block
            # transaction.sign_partial(payer)
            # transaction.sign_partial(recipient)
            # print('HERE2')
            # signature = client.send_transaction(transaction,recipient,payer, recent_blockhash=block)

            # print(f"Transaction Signature: {signature}")
        except Exception as ex:
            print(ex)
            print('Transit retry')
            time.sleep(1)




def get_latest_blockhash_with_retries(client):
    for attempt in range(1):
        try:
            blockhash = client.get_latest_blockhash().value.blockhash
            return blockhash
        except Exception as e:
            print(f"Failed to get latest blockhash: {e}")
            # time.sleep(2)  # Wait for 2 seconds before retrying

    return None

vault()
while True:
    schedule.run_pending()
    time.sleep(1)

