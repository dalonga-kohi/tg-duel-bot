import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from grouptypes import MsgType
from config import CHAT_ID, TOKEN

def MSG_START(stake: int, name: str):
   return f'The new Gulag has been started by <b>{name}</b>. Enter the Gulag for <b>{stake} $BOMBO</b>. \nFour more players can join this round. Are you brave enough to become\nthe champion of the Gulag? Join now for a chance to take the entire pot and earn the prestigious "CHAMPION" title!\n\nTo begin click button below'

def MSG_BEGIN_TIMER(stake: int, name: str):
    time = "5 minutes"

    return f'<b>{name}</b> is brave enough to try his luck in the Gulag. Winner takes entire pot {2*stake*0.99} $BOMBO and has to chance to get ”CHAMPION” title!\nTimer has started and you have <b>{time}</b> to grow balls and three more players can participate in this Gulag!'

def MSG_GAME(count: int, stake:int):
    return f'The Gulag is starting now! These {count} soldiers will fight for their life\n and the survivor wins this huge <b>{count * stake*0.99} $BOMBO</b> stack! Also the Winner will\nbe one step closer to upgrade his lifestyle from brokie to TOP G with a ROLEX on his wrist.'

def MSG_RESULT(stake: int, count: int, name: str):
    return f'This is unbeliveable <b>{name}</b> fought for his life and came out of the Gulag as the champion \nand takes the entire pot <b>{count * stake*0.99} $BOMBO</b>.\nIt looks like <b>{name}</b> is ready to fight for his new ROLEX and title of CHAMPION! Be like <b>{name}</b>.'

def MSG_CANCEL(game_id: int, name: str):
    return f'Unfortunately you all have no balls to risk your life and money.\nThe Gulag #{game_id} has been canceled and all deposits have been returned to players accounts.\n\nIf you feel brave today create new challenge or join to the existing one.'

URL_START = "res/start.gif"
URL_BEGIN_TIMER = "res/start.gif"
URL_GAME = "res/start.gif"
URL_RESULT = "res/start.gif"
URL_CANCEL = "res/start.gif"

async def send_group_msg(msg_type: MsgType, context: ContextTypes.DEFAULT_TYPE, game_id: int, user_id: int = 1, stake: int = 0, count: int = 0):
    username = get_username(user_id)

    if msg_type == MsgType.START:
        msg = MSG_START(name=username, stake=stake)
        url = URL_START
        kb = [
            [InlineKeyboardButton(text="Join to the Gulag", url=f"https://t.me/TestoDueloBot?start={game_id}")]
        ]
    elif msg_type == MsgType.BEGIN_TIMER:
        msg = MSG_BEGIN_TIMER(name=username, stake=stake)
        url = URL_BEGIN_TIMER
        kb = [
            [InlineKeyboardButton(text="Join to the Gulag", url=f"https://t.me/TestoDueloBot?start={game_id}")]
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
            [InlineKeyboardButton(text="Create new Gulag", url=f"https://t.me/TestoDueloBot?start")]
        ]
    elif msg_type == MsgType.CANCEL:
        msg = MSG_CANCEL(game_id=game_id, name=username)
        url = URL_CANCEL
        kb = [
            [InlineKeyboardButton(text="Create new Gulag", url=f"https://t.me/TestoDueloBot?start")]
        ]

    await context.bot.send_animation(chat_id=CHAT_ID, caption=msg, animation=url, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))


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