import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from grouptypes import MsgType
from config import BOT_USERNAME, CHAT_ID, TOKEN

def MSG_START(stake: int, name: str):
   return f'The new Gulag by <b>{name}</b> has started with pot of <b>{stake} $BOMBO</b>. <b>Four spots left</b> - hit button below to compete for the pot and the "CHAMPION" title!'

def MSG_BEGIN_TIMER(stake: int, name: str, count: int =2):
    time = "5 minutes"
    space = ""

    if count == 2:
        space = "for <b>three more to join!</b>"
    elif count == 3:
        space = "for <b>two more to join!</b>"
        time = "4 minutes"
    elif count == 4:
        space = "for <b>one more to join!</b>"
        time = "4 minutes"
    else:
        space = "<b>The Gulag is full.</b>"
        time = "4 minutes"

    return f'<b>{name}</b> has entered the Gulag. <b>Winner takes {count*int(stake)} $BOMBO</b> and the ”CHAMPION” title! <b>{time} left</b> ${space}'

def MSG_GAME(count: int, stake:int):
    return f"The Gulag begins now with <b>{count} fighters</b> battling for their lives to win a massive <b>{stake*count} $BOMBO</b> stack and take one step closer to upgrading from brokie to TOP G with a ROLEX on their wrist."

def MSG_RESULT(stake: int, count: int, name: str):
    return f"Unbelievably, <b>{name}</b> emerged as the Gulag champion, claiming the entire <b>{int(stake)*count} $BOMBO</b> and proving they're ready for a ROLEX and the CHAMPION title — be like {name}."

def MSG_CANCEL(game_id: int, name: str):
    return f'Unfortunately you all have no balls to risk your life and money. The Gulag #{game_id} has been canceled and all deposits have been returned to players accounts.\n\nIf you feel brave today create new challenge or join to the existing one.'

URL_START = "res/start.jpg"
URL_BEGIN_TIMER = "res/wait.jpg"
URL_GAME = "res/begin.jpg"
URL_RESULT = "res/win.jpg"
URL_CANCEL = "res/cancel.jpg"

async def send_group_msg(msg_type: MsgType, context: ContextTypes.DEFAULT_TYPE, game_id: int, user_id: int = 1, stake: int = 0, count: int = 0):
    username = get_username(user_id)

    stake = int(stake)

    if msg_type == MsgType.START:
        msg = MSG_START(name=username, stake=stake)
        url = URL_START
        kb = [
            [InlineKeyboardButton(text="Join to the Gulag", url=f"https://t.me/{BOT_USERNAME}?start={game_id}")]
        ]
    elif msg_type == MsgType.BEGIN_TIMER:
        msg = MSG_BEGIN_TIMER(name=username, stake=stake)
        url = URL_BEGIN_TIMER
        kb = [
            [InlineKeyboardButton(text="Join to the Gulag", url=f"https://t.me/{BOT_USERNAME}?start={game_id}")]
        ]
    elif msg_type == MsgType.BEGIN_JOIN:
        msg = MSG_BEGIN_TIMER(name=username, stake=stake, count=count)
        url = URL_BEGIN_TIMER
        kb = [
            [InlineKeyboardButton(text="Join to the Gulag", url=f"https://t.me/{BOT_USERNAME}?start={game_id}")]
        ]
    elif msg_type == MsgType.GAME:
        msg = MSG_GAME(stake=stake, count=count)
        url = URL_GAME
        kb = [
            []
        ]
    elif msg_type == MsgType.RESULT:
        msg = MSG_RESULT(stake=stake, count=count, name=username)
        url = URL_RESULT
        kb = [
            [InlineKeyboardButton(text="Create new Gulag", url=f"https://t.me/{BOT_USERNAME}?start")]
        ]
    elif msg_type == MsgType.CANCEL:
        msg = MSG_CANCEL(game_id=game_id, name=username)
        url = URL_CANCEL
        kb = [
            [InlineKeyboardButton(text="Create new Gulag", url=f"https://t.me/{BOT_USERNAME}?start")]
        ]

    await context.bot.send_photo(chat_id=CHAT_ID, caption=msg, photo=url, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))


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