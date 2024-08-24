from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, due: int, text: str) -> None:
    chat_id = update.effective_message.chat_id

    if due < 0:
        await update.effective_message.reply_text("Sorry we cannot go back to the future!")
        return

    job_removed = remove_job_if_exists(str(chat_id), context)

    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

    await update.effective_message.reply_text(text)
