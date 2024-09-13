import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import mysql.connector
import requests # type: ignore
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT, REPLY_NO_STATUS, TOKEN
from timer import get_time_left_in_job

mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)
r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)

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
mycursor = mydb.cursor()

async def show_status(game_id: int, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    mydb.commit()
    print(game_id)
    mycursor.execute(f"SELECT p1,p2,p3,p4,p5,stake,status,winner FROM games WHERE game_id='{game_id}'")
    results = mycursor.fetchall()
    count = 0
    if not results:
        await context.bot.send_message(chat_id=chat_id, text=REPLY_NO_STATUS, parse_mode='HTML', reply_markup=reply_markup)
        r.delete(chat_id)
        return

    for i in range(0,5):
        if results[0][i]:
            count = count + 1

    status = int(results[0][6])
    stake = int(results[0][5])
    stat = "No Data"
    if status == 9:
        stat = "Not paid"
    elif status == 1:
        stat = "Waiting for Start"
    elif stat == 2:
        stat = "Waiting for deposits"
    elif stat == 3:
        stat = "Ended"
    else:
        stat = "Canceled"

    if not results[0][7]:
        winner = "Not Determined"
    else:
        winner = get_username(results[0][7])

    left = get_time_left_in_job(job_name=f"start-{game_id}", context=context)
    if not left:
        time = "Timer not Started"
    else:
        time = f"{left} seconds"
    msg = f"<b>Status of the Gulag #{game_id}</b>\n\n\nStatus: {stat}\nStake: {stake}\nPot to Win: {stake*count}\nPlayers: {count}/5\nTime to start: {time}\nWinner: {winner}\n\n\nTo see and manage your games click 'My Gulags' from buttons below."
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML', reply_markup=reply_markup)
    r.delete(chat_id)


def get_kb(game_id: int):
    kb = [
            InlineKeyboardButton(f"❌ Quit Gulag #{game_id}", callback_data=f'cancel-{game_id}'),
    ]
    return kb
async def show_games_pending(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    mydb.commit()

    kb = []

    mycursor.execute(f"SELECT game_id, stake, p1,p2,p3,p4,p5 FROM games WHERE (status=1 OR status=2) AND (p1='{user_id}' OR p2='{user_id}' OR p3='{user_id}' OR p4='{user_id}' OR p5='{user_id}')")
    results = mycursor.fetchall()

    if not results:
        await context.bot.sendMessage(chat_id=user_id, text="<b>No gulags found.</b>\n\n\nNo worries, you can choose one of the options below and start playing 🕹️", reply_markup=reply_markup, parse_mode='HTML')
        return
    msg = "<b>Pending Gulags:</b>\n\n"
    for r in results:
        kb.append(get_kb(r[0]))

        stake = int(r[1])
        count = 0
        for i in range(2,7):
            if r[i]:
                count = count + 1

        left = get_time_left_in_job(job_name=f"start-{r[0]}", context=context)
        if not left:
            time = "Timer not Started"
        else:
            time = f"{left} seconds"

        msg += f"<b>Gulag #{r[0]}</b>\n\tStake: {stake}\n\tPot to Win: {stake*count}\n\tPlayers: {count}/5\n\tTime to start: {time}\n\n\n"
        reply = InlineKeyboardMarkup(kb)

    await context.bot.sendMessage(chat_id=user_id, text=msg, reply_markup=reply, parse_mode='HTML')

async def show_games_canceled(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    mydb.commit()


    mycursor.execute(f"SELECT game_id, stake, p1,p2,p3,p4,p5 FROM games WHERE (status=4) AND (p1='{user_id}' OR p2='{user_id}' OR p3='{user_id}' OR p4='{user_id}' OR p5='{user_id}')")
    results = mycursor.fetchall()

    if not results:
        await context.bot.sendMessage(chat_id=user_id, text="<b>No gulags found.</b>\n\n\nNo worries, you can choose one of the options below and start playing 🕹️", reply_markup=reply_markup, parse_mode='HTML')
        return

    msg = "<b>Canceled Gulags:</b>\n\n"
    for r in results:
        stake = int(r[1])
        count = 0
        for i in range(2,7):
            if r[i]:
                count = count + 1

        msg += f"<b>Gulag #{r[0]}</b>\n\tStake: {stake}\n\tPlayers: {count}/5\n\n\n"
    reply = [
        [InlineKeyboardButton("🔙 Go Back",callback_data=f'back-1')]
    ]
    await context.bot.sendMessage(chat_id=user_id, text=msg, reply_markup=InlineKeyboardMarkup(reply), parse_mode='HTML')

async def show_games_won(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    mydb.commit()


    mycursor.execute(f"SELECT game_id, stake, p1,p2,p3,p4,p5 FROM games WHERE status=3 AND winner='{user_id}'")
    results = mycursor.fetchall()

    if not results:
        await context.bot.sendMessage(chat_id=user_id, text="<b>No gulags found.</b>\n\n\nNo worries, you can choose one of the options below and start playing 🕹️", reply_markup=reply_markup, parse_mode='HTML')
        return

    msg = "<b>Won Gulags:</b>\n\n"
    for r in results:
        stake = int(r[1])
        count = 0
        for i in range(2,7):
            if r[i]:
                count = count + 1

        msg += f"<b>Gulag #{r[0]}</b>\n\tStake: {stake}\n\tPlayers: {count}/5\n\tPot: {stake*count} $BOMBO\n\n\n"
    reply = [
        [InlineKeyboardButton("🔙 Go Back",callback_data=f'back-1')]
    ]
    await context.bot.sendMessage(chat_id=user_id, text=msg, reply_markup=InlineKeyboardMarkup(reply), parse_mode='HTML')

async def show_games_lost(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    mydb.commit()


    mycursor.execute(f"SELECT game_id, stake, p1,p2,p3,p4,p5, winner FROM games WHERE status=3 AND winner <> '{user_id}' AND (p1='{user_id}' OR p2='{user_id}' OR p3='{user_id}' OR p4='{user_id}' OR p5='{user_id}')")
    results = mycursor.fetchall()

    if not results:
        await context.bot.sendMessage(chat_id=user_id, text="<b>No gulags found.</b>\n\n\nNo worries, you can choose one of the options below and start playing 🕹️", reply_markup=reply_markup, parse_mode='HTML')
        return

    msg = "<b>Lost Gulags:</b>\n\n"
    for r in results:
        stake = int(r[1])
        count = 0
        for i in range(2,7):
            if r[i]:
                count = count + 1

        winner = get_username(r[7])
        msg += f"<b>Gulag #{r[0]}</b>\n\tStake: {stake}\n\tPlayers: {count}/5\n\tPot: {stake*count*0.99} $BOMBO\n\tWinner: {winner}\n\n\n"
    reply = [
        [InlineKeyboardButton("🔙 Go Back",callback_data=f'back-1')]
    ]
    await context.bot.sendMessage(chat_id=user_id, text=msg, reply_markup=InlineKeyboardMarkup(reply), parse_mode='HTML')

def get_username(user_id: int):
    url = f'https://api.telegram.org/bot{TOKEN}/getChat?chat_id={user_id}'
    response = requests.get(url)
    data = response.json()
    if data['ok']:
        winner = data['result'].get('username')
        if not winner:
            winner = data['result'].get('first_name')
        print(f'Username: {winner}')
    else:
        print(f"Error: {data['description']}")
        winner = "Anonymous"
    return winner