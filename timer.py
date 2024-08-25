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
    user_id = job.name.split("-")[1]  # Extract user_id from job name
    game_id = job.name.split("-")[2]  # Extract game_id from job name

    print(f"GAMEID: {game_id}")
    print(f"USERID: {user_id}")

    # Check if the user has confirmed the deposit

    status = r.get(user_id)

    if status == "DEPOSIT":  # User hasn't confirmed deposit
        # Remove the player from the game (same logic as before)

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT p1, p2, p3, p4, p5 FROM games WHERE game_id={game_id}")
        myresult = mycursor.fetchone()

        player_removed = False
        for x in myresult[:5]:
            if x == user_id:
                mycursor.execute(f"UPDATE games SET p{x}=NULL WHERE game_id='{game_id}'")
                print(f"index: {x} player: {user_id} gameid: {game_id}")
                player_removed = True
                break

        if player_removed:
            mydb.commit()

            # Notify the player that they were kicked out
            await context.bot.send_message(job.chat_id, text=f"Time is up! You didn't confirm your deposit and have been removed from the game.")

            # Notify other players that the user has been kicked
            for x in myresult:
                if x and x != int(user_id):
                    await context.bot.send_message(job.chat_id, text=f"Player {user_id} has been removed from the game due to failure to confirm deposit.")
            
            # Cleanup
            r.delete(user_id)

        else:
            await context.bot.send_message(job.chat_id, text=f"Error: Could not remove player {user_id} from the game.")
    
    else:
        print(f"Player {user_id} payed the deposit")
        await context.bot.send_message(job.chat_id, text=f"Thank you! Your deposit was confirmed in time.")

async def send_warning(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    user_id = job.name.split("-")[2]  # Extract user_id from job name

    print(f"User {user_id} has 30s to confirm deposit")

    # Send a warning message
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

    if due < 0:
        await update.effective_message.reply_text("Sorry we cannot go back to the future!")
        return

    # Remove previous jobs, if any
    job_removed = remove_job_if_exists(str(chat_id), context)

    # Schedule the main timer (4 minutes)
    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=job_name, data=due)

    # Schedule the warning timer (3 minutes 30 seconds)
    warning_due = due - 30  # Warning triggers 30 seconds before due time
    warning_job_name = f"warning-{job_name}"
    context.job_queue.run_once(send_warning, warning_due, chat_id=chat_id, name=warning_job_name)

    # Notify user
    if text:
        await update.effective_message.reply_text(text)
