from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from config import CMD_DUEL, REPLY_DUEL, REPLY_HELP, TOKEN, BOT_USERNAME, CMD_START, CMD_HELP, REPLY_START

async def handle_cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_START)
    await update.message.reply_photo('https://picsum.photos/200')

async def handle_cmd_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_DUEL)

async def handle_cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(REPLY_HELP)