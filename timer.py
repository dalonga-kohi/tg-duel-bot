from telegram import Update
from telegram.ext import ContextTypes
from datetime import timedelta
import redis
from config import R_HOST, R_PORT, MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB
import mysql.connector

r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)
mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    
    username = job.data["username"]
    user_id = job.data["user_id"]
    game_id = job.name.split("-")[2]
    chat_id = job.data["chat_id"]

    status = r.get(user_id)

    if status == "DEPOSIT":
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT p1, p2, p3, p4, p5 FROM games WHERE game_id={game_id}")
        myresult = mycursor.fetchone()


        player_removed = False
        p_index=0
        for x in myresult[:5]:
            p_index += 1
            if x:
                if int(x) == int(user_id):
                    mycursor.execute(f"UPDATE games SET p{p_index}=NULL WHERE game_id={game_id}")
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
            await context.bot.send_message(job.chat_id, text=f"Error: Could not remove player {username} from the game.")
    
    else:
        print(f"Player {user_id} payed the deposit")
        await context.bot.send_message(job.chat_id, text=f"Thank you! Your deposit was confirmed in time.")

async def send_warning(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    user_id = job.name.split("-")[2]

    print(f"User {user_id} has 30s to confirm deposit")

    await context.bot.send_message(job.chat_id, text=f"Warning: You have 30 seconds left to confirm your deposit!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, due: int, text: str | None, job_name: str) -> None:
    chat_id = update.effective_message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.first_name

    job_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "username": username
    }

    if due < 0:
        await update.effective_message.reply_text("Sorry we cannot go back to the future!")
        return

    job_removed = remove_job_if_exists(str(chat_id), context)

    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=job_name, data=job_data)

    warning_due = due - 30
    warning_job_name = f"warning-{job_name}"
    context.job_queue.run_once(send_warning, warning_due, chat_id=chat_id, name=warning_job_name, data=job_data)

    if text:
        await update.effective_message.reply_text(text)
