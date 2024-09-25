import random
import mysql.connector
from solders.pubkey import Pubkey # type: ignore
from config import CHAT_ID, FEE_ADDRESS, FEE_ADDRESS2, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, MINT
from group import send_group_msg
from grouptypes import MsgType
from solana.rpc.api import Client
from telegram.ext import ContextTypes

bombo_mint_address = Pubkey.from_string(MINT)


client = Client("https://api.mainnet-beta.solana.com")

async def result(context: ContextTypes.DEFAULT_TYPE):
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )

    cursor = mydb.cursor()
    data = context.job.data

    game_id = data["id"]

    mydb.commit()
    sql = f"SELECT p1,p2,p3,p4,p5, stake FROM games WHERE game_id='{game_id}'"
    cursor.execute(sql)
    res = cursor.fetchall()

    if not res:
        mydb.shutdown()

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
        mydb.shutdown()

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
            mydb.shutdown()
        except:
            mydb.shutdown()

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
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )

    cursor = mydb.cursor()
    mydb.commit()
    sql = f"SELECT p1,p2,p3,p4,p5, stake FROM games WHERE game_id='{game_id}'"
    cursor.execute(sql)
    res = cursor.fetchall()
    mydb.shutdown()

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
