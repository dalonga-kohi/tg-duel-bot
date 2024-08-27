from enum import Enum

class MsgType(Enum):
    START = 1
    CANCEL = 2
    BEGIN_TIMER = 3
    GAME = 4
    RESULT = 5