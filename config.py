TOKEN = '7311308484:AAESuIrjxAvXuwxK7vz6Fh7e8NWVMwR7zXs'
BOT_USERNAME = '@TestoDueloBot'

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

REPLY_START = "Howdy! I'm the Duel Bot 🤖⚔️. To begin just select one of the commands or type /info for further info 😘"
REPLY_DUEL = 'Please provide the stake of the challenege in $BOMBO tokens:'
REPLY_CANCEL = '⛑️'
REPLY_STATUS = 'Status'
REPLY_JOIN = 'To join type the id of the challenge:'
REPLY_NO_JOIN = 'Not even a single challenge with the id provided 🙈.\nTry again'
REPLY_NO_GAME = 'You can create a new game with /duel or join with /join. You can also type /info to learn more about the game 🕹️'
REPLY_WRONG_STAKE = '🚨 Provided value is invalid \n Make sure it is a plain number 🔢'
REPLY_NO_FREE = 'No free seats left for you 😞\n You can join to the other game or create your own with /challenge'
REPLY_ALREADY_WD = 'Someone else is currently depositing.\nPlease wait a moment and try again by tapping <strong>"Try Again"</strong>'