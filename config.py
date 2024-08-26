TOKEN = '7311308484:AAESuIrjxAvXuwxK7vz6Fh7e8NWVMwR7zXs'
BOT_USERNAME = '@TestoDueloBot'
CHAT_ID = '-1002233858008'

MIN_STAKE = 5000
MAX_STAKE = 500000000

#DB
R_HOST='localhost'
R_PORT=6379
MYSQL_HOST='localhost'
MYSQL_DB='duel_test'
MYSQL_USER='root'
MYSQL_PASS=''

CMD_START = 'start'
CMD_DUEL = 'challenge'
CMD_JOIN = 'join'
CMD_STATUS = 'status'
CMD_CANCEL = 'cancel'

REPLY_GAME_END = "The game has already ended.\n\nYour deposit has been transfered to your account address. \nTo withdraw select 'My Account' and then 'Withdraw'"
REPLY_START = "Howdy! I'm the Duel Bot 🤖⚔️. To begin just select one of the commands 😘"
REPLY_DUEL = f'Please provide the stake of the challenege that ranges from\n <b>{MIN_STAKE} to {MAX_STAKE}</b> $BOMBO tokens:'
REPLY_CANCEL = '⛑️'
REPLY_STATUS = 'Status'
REPLY_JOIN = 'To join type the id of the challenge:'
REPLY_NO_JOIN = 'Not even a single challenge with the id provided 🙈.\nTry again:'
REPLY_NO_GAME = 'You can create a new game with /challenge or join with /join. You can also type /start to learn more about the game 🕹️'
REPLY_WRONG_STAKE = '🚨 Provided value is invalid \n Make sure it is a plain number 🔢 and try again'
REPLY_NO_FREE = 'No free seats left for you 😞\n You can join to the other game or create your own with /challenge'
REPLY_ALREADY_WD = 'Someone else is currently depositing.\nPlease wait a moment and try again by tapping <strong>"Try Again"</strong>'
REPLY_ABAN = "<b>You have canceled game creation!</b>\n\nIf you have deposited any tokens to the deposit address, you can withdraw them by clicking 'My Account'\n\n\n Don't worry you can still create new challenge or join to an existing game."
RULES = 'BLA BLA'