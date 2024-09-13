import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import BOT_USERNAME, MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, R_HOST, R_PORT, REPLY_CANCEL, REPLY_DUEL, REPLY_JOIN, REPLY_NO_FREE, REPLY_NO_JOIN, REPLY_STATUS, REPLY_START, T_GAME, T_PLAYER
import mysql.connector
from solders.keypair import Keypair # type: ignore
from group import send_group_msg
from grouptypes import MsgType
from timer import set_player_timer, set_start_game_timer

r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)
mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)


async def reject_cmd(update: Update):
    kb = [
        [InlineKeyboardButton(text="Create new Gulag", url=f"https://t.me/{BOT_USERNAME}?start")]
    ]
    await update.message.reply_text('You can access all bot functions via private chat. Hit button below to see what Gulag bot has to offer.', parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
    return

async def handle_cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.chat.type

    if type != "private":
        await reject_cmd(update)
        return

    if context.args:
        user_id = update.message.from_user.id
        status = r.get(user_id)

        if status:
            await update.message.reply_text('You have started another task before make sure you are not currently joining to some gulag or creating one.')
            return
        print(f"Args: {context.args[0]}")
        await join(user_id=user_id, update=update, game_id=context.args[0],context=context)
        return

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
    await update.message.reply_markdown_v2(REPLY_START, reply_markup=reply_markup)

async def handle_cmd_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.chat.type

    if type != "private":
        await reject_cmd(update)
        return

    user_id = update.message.from_user.id
    status = r.get(user_id)

    if status:
        await update.message.reply_text('You have started another task before make sure you are not currently joining to some gulag or creating one.')
        return

    print(f'New duel by user {user_id}')
    r.set(f'{user_id}', 'SETTING')
    keyboard = [
        [InlineKeyboardButton("❌ Cancel Gulag", callback_data=f'abandon-nogame')],
    ]
    await update.message.reply_text(REPLY_DUEL, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def handle_cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.chat.type

    if type != "private":
        await reject_cmd(update)
        return

    user_id = update.message.from_user.id
    status = r.get(user_id)
    if status:
        await update.message.reply_text('You have started another task before make sure you are not currently joining to some gulag or creating one.')
        return

    r.set(f'{user_id}', 'STATUS')
    await update.message.reply_text(REPLY_STATUS)

async def handle_cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.chat.type

    if type != "private":
        await reject_cmd(update)
        return

    user_id = update.message.from_user.id
    print(f'Join by user {user_id}')
    status = r.get(user_id)

    if status:
        await update.message.reply_text('You have started another task before make sure you are not currently joining to some gulag or creating one.')
        return

    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-nogame')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    r.set(f'{user_id}', 'JOINING')
    await update.message.reply_text(REPLY_JOIN, reply_markup=reply_markup)

async def join(update, game_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    r.set(user_id, 'JOINING')
    mydb.commit()
    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT p1,p2,p3,p4,p5,status,stake FROM games WHERE game_id={game_id}")
    myresult = mycursor.fetchall()

    if not myresult:
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-nogame')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(REPLY_NO_JOIN, parse_mode='HTML', reply_markup=reply_markup)
        return
    if myresult[0][5] != 1:
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-nogame')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(REPLY_NO_JOIN, parse_mode='HTML', reply_markup=reply_markup)
        return
    myresult = myresult[0]
    print(myresult)

    isFree = False
    p_index = 0
    for x in myresult[:5]:
        try:
            if int(x) == user_id:
                keyboard = [
                    [
                        InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
                        InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
                    ],
                    [
                        InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
                    ],
                    [
                        InlineKeyboardButton("🆕 Create new Gulag", callback_data=f'create-{user_id}'),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("<strong>You are already in that gulag</strong>\n\n You can still join to other gulags or create another one.", parse_mode='HTML', reply_markup=reply_markup)
                r.delete(user_id)
                return
        except:
            pass

        p_index = p_index + 1
        if x == None:
            isFree = True
            break

    if not isFree:
        keyboard = [
            [
                InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
                InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
            ],
            [
                InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
            ],
            [
                InlineKeyboardButton("🆕 Create new Gulag", callback_data=f'create-{user_id}'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(REPLY_NO_FREE, parse_mode='HTML', reply_markup=reply_markup)
        r.delete(user_id)
        return

    if myresult[5] == 2:
        keyboard = [
            [
                InlineKeyboardButton("👤 My Account", callback_data=f'account-{user_id}'),
                InlineKeyboardButton("⚔️ My Gulags", callback_data=f'games'),
            ],
            [
                InlineKeyboardButton("📜 Read Rules of the Game", callback_data=f'rules'),
            ],
            [
                InlineKeyboardButton("🆕 Create new Gulag", callback_data=f'create-{user_id}'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        r.delete(user_id)
        await update.message.reply_text('<strong>Gulag has already begun.</strong>\n\nNo worries, you can choose one of the options below and start playing 🕹️', parse_mode='HTML', reply_markup=reply_markup)
        return

    keypair = Keypair()

    public_key = keypair.pubkey()

    private_key = keypair.secret()
    print(f"Public Key: {public_key}")
    print(f"Private Key: {private_key.hex()}")

    mycursor = mydb.cursor()
    sql = f"UPDATE games SET p{p_index}='{user_id}' WHERE game_id='{game_id}'"
    mycursor.execute(sql)
    sql = "INSERT INTO wallets (user_id, game_id, pub_key, priv_key) VALUES (%s, %s, %s, %s)"
    val = (user_id, game_id, f'{public_key}', private_key.hex())
    mycursor.execute(sql, val)

    mydb.commit()
    keyboard = [
        [
            InlineKeyboardButton("💸 Confirm Deposit", callback_data=f'confirm-{game_id}'),
            InlineKeyboardButton("❌ Cancel", callback_data=f'stopj-{game_id}')
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f'Your deposit address is:\n<code class="monospace-text">{public_key}</code>\n \n \nTo join send {myresult[6]} $BOMBO to this address.\nThen tap <strong>"Confirm Deposit"</strong> to begin.\n\n You have 4 minutes to confirm the deposit.', reply_markup=reply_markup, parse_mode='HTML')

    r.set(user_id, "DEPOSIT")

    await set_player_timer(update=update, context=context, due=T_PLAYER, text=None, job_name=f'deposit-{user_id}-{game_id}')
