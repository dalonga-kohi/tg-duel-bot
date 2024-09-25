from telegram import Update
from telegram.ext import ContextTypes
from datetime import timedelta
import redis
from config import R_HOST, R_PORT, MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB, T_PLAYER
import mysql.connector
from datetime import datetime, timezone

from game import start_game
from refounds import cancel, stop_join

r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)


async def check_full_players(game_id: str, context) -> None:
    pass
    # players = 0
    # mydb.commit()
    # mycursor = mydb.cursor()
    # mycursor.execute(f"SELECT p1,p2,p3,p4,p5,status,stake FROM games WHERE game_id={game_id}")
    # myresult = mycursor.fetchall()

    # for x in range(0,5):
    #     try:
    #         if myresult[0][x] and r.get(x) != "DEPOSIT":
    #             players += 1
    #     except:
    #         pass

    # if players == 5:
    #     jobs = context.job_queue.get_jobs_by_name(f"start-{game_id}")
    #     for j in jobs:
    #         j.schedule_removal()
    #     await start_game(game_id, context)

async def send_game_warning(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    chat_id = job.data["chat_id"]
    game_id = job.name.split("-")[2]

    print(game_id)

    players = 0
    mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
    )
    mydb.commit()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT p1,p2,p3,p4,p5,status,stake FROM games WHERE game_id={game_id}")
    myresult = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    if myresult[0][5] == 4:
        return

    for x in range(0,5):
        try:
            if myresult[0][x]:
                players += 1
        except:
            pass

    print(f"Players: {players}")

    if players >= 2:
        for x in range(0,5):
            try:
                if myresult[0][x]:
                    await context.bot.send_message(chat_id=myresult[0][x], text=f"The game will start in 30 seconds")
            except:
                pass
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"The game needs at least 2 players, it will be cancelled in 30 seconds")

async def player_alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    mydb = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB
    )
    username = job.data["username"]
    user_id = job.data["user_id"]
    game_id = job.name.split("-")[2]
    chat_id = job.data["chat_id"]

    status = r.get(user_id)

    if status == "DEPOSIT":
        mydb.commit()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT p1, p2, p3, p4, p5,status FROM games WHERE game_id={game_id}")
        myresult = mycursor.fetchone()

        if myresult[0][5] == 4:
            return

        player_removed = False
        p_index=0
        for x in myresult[:5]:
            p_index += 1
            if x:
                if int(x) == int(user_id):
                    await stop_join(game_id, user_id, chat_id, context)
                    player_removed = True
                    break

        if player_removed:
            mydb.commit()

            print(f"Player {user_id} has been kicked out the game")
            await context.bot.send_message(job.chat_id, text=f"Time is up! You didn't confirm your deposit and have been removed from the game.")

            for x in myresult:
                if x:
                    if int(x) != int(user_id):
                        await context.bot.send_message(chat_id=x, text=f"Player {username} has been removed from the game due to failure to confirm deposit.")

            r.delete(user_id)

        else:
            # await context.bot.send_message(job.chat_id, text=f"Error: Could not remove player {username} from the game.")
            pass

    else:
        print(f"Player {user_id} payed the deposit")
        await check_full_players(game_id, context)

async def get_players_with_deposit(game_id) -> int:
    players = 0
    mydb = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB
    )
    mydb.commit()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT p1,p2,p3,p4,p5,status FROM games WHERE game_id={game_id}")
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    if not myresult:
        return 0

    if myresult[0][5] == 4:
        return 0
    for x in myresult[0][:5]:
        try:
            print(f"Check depo: {x}")
            if int(x) != 0 and r.get(x) != "DEPOSIT":
                players += 1
        except:
            pass

    return players

async def game_alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job

    game_id = job.name.split("-")[1]
    chat_id = job.data["chat_id"]

    players = await get_players_with_deposit(game_id)

    if players == 0:
        return

    print(f"Players with deposit: {players}")
    if players >= 2:
        await start_game(game_id, context)
    else:
        mydb = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB
        )
        mydb.commit()
        cursor = mydb.cursor()
        cursor.execute(f"SELECT p1,p2,p3,p4,p5 FROM games WHERE game_id='{game_id}'")
        r = cursor.fetchall()
        cursor.close()
        mydb.close()

        if not r:
            return

        owner = r[0]
        await cancel(chat_id=chat_id, context=context, game_id=game_id, user_id=owner)

def get_time_left_in_job(job_name: str, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    current_jobs = context.job_queue.get_jobs_by_name(job_name)

    if current_jobs:
        job = current_jobs[0]

        current_time = datetime.now(timezone.utc)  # Get the current UTC time
        time_left = job.next_t - current_time  # Calculate the time left as a timedelta

        # Convert the time left to seconds and ensure it's a positive value
        time_left_seconds = int(time_left.total_seconds())

        if time_left_seconds > 0:
            return time_left_seconds  # Return time left in seconds as an integer
        else:
            return None  # Job has expired or very close to execution
    else:
        return None  # No active job found

async def send_player_warning(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    user_id = job.name.split("-")[2]

    status = r.get(user_id)

    if status != 'DEPOSIT':
        return

    print(f"User {user_id} has 30s to confirm deposit")

    # await context.bot.send_message(job.chat_id, text=f"Warning: You have 30 seconds left to confirm your deposit!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

# async def modify_game_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, new_due: int, job_name: str, text: str) -> None:
#     chat_id = update.effective_message.chat_id
#     user_id = update.message.from_user.id
#     username = update.message.from_user.first_name

#     job_data = {
#         "chat_id": chat_id,
#         "user_id": user_id,
#         "username": username
#     }

#     job_removed = remove_job_if_exists(job_name, context)

#     context.job_queue.run_once(alarm, new_due, chat_id=chat_id, name=job_name, data=job_data)

#     warning_due = new_due - 30
#     warning_job_name = f"warning-{job_name}"
#     context.job_queue.run_once(send_warning, warning_due, chat_id=chat_id, name=warning_job_name, data=job_data)

#     for x in range(0,5):
#         try:
#             if myresult[0][x]:
#                 await context.bot.send_message(chat_id=myresult[0][x], text=text)
#         except:
#             pass

async def set_player_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, due: int, text: str | None, job_name: str) -> None:
    chat_id = update.effective_message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.first_name

    game_id = job_name.split("-")[1]

    job_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "username": username
    }

    if due < 0:
        await update.effective_message.reply_text("Sorry we cannot go back to the future!")
        return

    time_left = get_time_left_in_job(job_name=f"start-{game_id}", context=context)

    print(f"TIME: {time_left}")

    if time_left and time_left < T_PLAYER:
        await modify_game_timer(update, context, new_due=due, job_name=f"start-{game_id}", text="Game queue will be increased to 4 mins due to player deposit")


    context.job_queue.run_once(player_alarm, due, chat_id=chat_id, name=job_name, data=job_data)

    warning_due = due - 30
    warning_job_name = f"warning-{job_name}"
    context.job_queue.run_once(send_player_warning, warning_due, chat_id=chat_id, name=warning_job_name, data=job_data)

    if text:
        await update.effective_message.reply_text(text)

async def modify_game_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, new_due: int, job_name: str, text: str) -> None:
    chat_id = update.effective_message.chat_id

    existing_jobs = context.job_queue.get_jobs_by_name(job_name)

    if not existing_jobs:
        await update.effective_message.reply_text("No active timer to modify!")
        return

    current_job = existing_jobs[0]
    current_remaining_time = current_job.next_t - context.application.time

    remove_job_if_exists(job_name, context)

    job_data = { "chat_id": chat_id }
    context.job_queue.run_once(game_alarm, new_due, chat_id=chat_id, name=job_name, data=job_data)

    if new_due > 30:
        warning_due = new_due - 30
        warning_job_name = f"warning-{job_name}"
        context.job_queue.run_once(send_game_warning, warning_due, chat_id=chat_id, name=warning_job_name, data=job_data)

    # for x in range(0,5):
    #     try:
    #         if myresult[0][x]:
    #             await context.bot.send_message(chat_id=myresult[0][x], text=text)
    #     except:
    #         pass


async def set_start_game_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, due: int, text: str, job_name: str, game_id: int) -> None:
    chat_id = update.effective_message.chat_id

    job_data = { "chat_id": chat_id }

    if due < 0:
        await update.effective_message.reply_text("Sorry we cannot go back to the future!")
        return

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(game_alarm, due, chat_id=chat_id, name=job_name, data=job_data)

    warning_due = due - 30
    warning_job_name = f"warning-{job_name}"
    context.job_queue.run_once(send_game_warning, warning_due, chat_id=chat_id, name=warning_job_name, data=job_data)

    # mycursor = mydb.cursor()
    # mycursor.execute(f"SELECT p1, p2, p3, p4, p5 FROM games WHERE game_id={game_id}")
    # myresult = mycursor.fetchone()

    # for x in range(0,5):
    #     try:
    #         if myresult[0][x]:
    #             await context.bot.send_message(chat_id=myresult[0][x], text=text)
    #     except:
    #         pass
