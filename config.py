TOKEN = '7075703461:AAHrvCpQaFoqdWvHivVogJ93_0ikWDdwgao'
MINT = "D3pmeo4MrV2eWMJH3WybR4fnKdMiSS4DrYHqdYNNjQU5"
DECIMALS = 9
TOKEN_NAME = "BOMBO"
BOT_USERNAME = 'BomboGulag_Bot'
CHAT_ID = '-1002055858151'
FEE_ADDRESS = "8yoANdy68RvXXXHJ36Gzxb1N6wTaPHnEg23wJY6UTcqe"
FEE_ADDRESS2 = "8yoANdy68RvXXXHJ36Gzxb1N6wTaPHnEg23wJY6UTcqe"
VAULT = "2JLM5dd7VXL1dVoToM2vUP3DwyvTVtnatTeGDwLumx6u"
VAULT_PRIV = "ffdd857f2960105b5605066aabe6dc29262f3c724485139c8893e82e0fb07e6e"
MIN_STAKE = 5000
MAX_STAKE = 500000000
T_PLAYER = 60*4
T_GAME = 60*5
PAYER = "583bc2e6fa0a84c881e5ae21a3a74c213e2ced902b3be64b268a3d007cd9ee9a"
#DB
R_HOST='localhost'
R_PORT=6379
MYSQL_HOST='localhost'
MYSQL_DB='duel_test'
MYSQL_USER='root'
MYSQL_PASS=''

CMD_START = 'start'
CMD_DUEL = 'gulag'
CMD_JOIN = 'join'
CMD_STATUS = 'status'
CMD_CANCEL = 'cancel'

RULES = '''
The game "Gulag" is a high\-stakes multiplayer game where one player, known as the *Gulag Creator*, initiates a new game by creating a "Gulag" with four open slots and setting a specific stake in tokens that each player must deposit to participate\. The process is as follows:

1\. *Gulag Creation*: The Gulag Creator sets up a new game by defining the required token deposit and opens four slots for other players to join\. A message announcing the creation of the Gulag is displayed in the main chat, alerting other players to the opportunity\.

2\. *Player Joining*: Once the Gulag is created, other players can join the game by occupying one of the four available slots\. As soon as the first player joins and makes their deposit, a 5\-minute timer starts\. During this period, other players must join and claim the remaining slots\.

3\. *Deposit Phase*: After joining, each player has 4 minutes to deposit the required amount of tokens as specified by the Gulag Creator\. If a player fails to make the deposit within this timeframe, they are automatically kicked out of the game, and their slot may become available for another player to take\.

4\. *Game Start*: The game officially begins once all players have made their deposits\. At this point, the total prize pool consists of the sum of all players' deposits, minus a 1\.5% fee\.

5\. *Winner Selection*: The game randomly selects one of the participating players as the winner\. This player receives the entire prize pool, which is the sum of all deposits after the fee deduction\.

'''
REPLY_GAME_END = "The gulag has already ended.\n\nYour deposit has been transfered to your account address. \nTo withdraw select 'My Account' and then 'Withdraw'"
REPLY_START = "Welcome to the game\! I'm the gulag Bot 🤖⚔️\."+'\n\n'+'"Gulag" is a multiplayer game where one player creates a new game with four open slots and sets a required token deposit\. Other players join and must deposit the set amount within a limited time\. If a player fails to deposit, they are kicked out of the game\. Once all players have made their deposits, a winner is randomly selected to win the total prize pool, minus a 1\.5% fee\.' + "\n\nTo begin just select one of the commands 😘"
REPLY_DUEL = f'Please provide the stake of the gulag that ranges from\n <b>{MIN_STAKE} to {MAX_STAKE}</b> ${TOKEN_NAME} tokens:'
REPLY_CANCEL = '⛑️'
REPLY_STATUS = 'To see a status enter a gulag id:'
REPLY_JOIN = 'To join type the id of the gulag:'
REPLY_NO_STATUS = "Not even a single gulag with the id provided 🙈.\n\n\nTo see and manage your gulags click 'My Gulags' from buttons below."
REPLY_NO_JOIN = 'Not even a single gulag with the id provided 🙈.\nTry again:'
REPLY_NO_GAME = 'You can create a new gulag with /gulag or join with /join. You can also type /start to learn more about the gulag 🕹️'
REPLY_WRONG_STAKE = '🚨 Provided value is invalid \n Make sure it is a plain number 🔢 and try again'
REPLY_NO_FREE = 'No free seats left for you 😞\n You can join to the other gulag or create your own with /gulag'
REPLY_ALREADY_WD = 'Someone else is currently depositing.\nPlease wait a moment and try again by tapping <strong>"Try Again"</strong>'
REPLY_ABAN = "<b>You have canceled gulag creation!</b>\n\nIf you have deposited any tokens to the deposit address, you can withdraw them by clicking 'My Account'\n\n\n Don't worry you can still create new gulag or join to an existing gulag."
