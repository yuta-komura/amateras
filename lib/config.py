from enum import Enum

PROJECT_DIR = __file__.replace("/lib/config.py", "")


class Virtual(Enum):
    class Trade(Enum):
        ASSET = 100000
        PROFIT_TARGET = 1
        LOSSCUT_TARGET = -1
        TIME_FRAME = 30  # minutes
        CHANNEL_WIDTH = 5


class AssetManagement(Enum):
    EXECUTE_TIME = 23


class DATABASE(Enum):
    class TRADINGBOT(Enum):
        HOST = '*********'
        USER = '*********'
        PASSWORD = '*********'
        DATABASE = '*********'


class Bitflyer(Enum):
    class Api(Enum):
        KEY = "*********"
        SECRET = "*********"

    class User(Enum):
        LOGIN_ID = "*********"
        PASSWORD = "*********"


class CoinApi(Enum):
    KEY = "*********"


class DirPath(Enum):
    PROJECT = PROJECT_DIR
    IMG = PROJECT_DIR + "/img"


class FilePath(Enum):
    WARNING_MP3 = PROJECT_DIR + "/sound/WARNING.mp3"
    ERROR_MP3 = PROJECT_DIR + "/sound/ERROR.mp3"
    SYSTEM_LOG = PROJECT_DIR + "/log/system.log"
    AA = PROJECT_DIR + "/document/AA.txt"
    CHROMEDRIVER = PROJECT_DIR + "/chromedriver"
