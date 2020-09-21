import inspect
import os
from datetime import datetime
from logging import DEBUG, FileHandler, Formatter, StreamHandler, getLogger

from pytz import timezone, utc

from lib.config import DirPath, FilePath
from lib.mysql import MySQL


def play_sound(path: str):
    play_command = "mpg123 -q {path}".format(path=path)
    os.system(play_command)


def get_file_path():
    cal_frame = inspect.getouterframes(inspect.currentframe(), 2)
    return cal_frame[2][1], cal_frame[2][2]


def tuple_to_string(t: tuple):
    s = None
    for i in range(len(t)):
        if i == 0:
            s = str(t[0])
            continue
        s += " " + str(t[i])
    return s


def content_formatter(content: str):
    if len(content) > content_size:
        content = content[:content_size - 3] + "..."
    return content


def info(*contents):
    content = tuple_to_string(contents)
    content = content_formatter(content)
    file_path = str(get_file_path()).replace(DirPath.PROJECT.value, "")
    logger.info(msg=content, extra={'file_path': file_path})


def warning(*contents):
    content = tuple_to_string(contents)
    file_path = str(get_file_path()).replace(DirPath.PROJECT.value, "")
    logger.warning(msg=content, extra={'file_path': file_path})
    play_sound(FilePath.WARNING_MP3.value)


def error(*contents):
    content = tuple_to_string(contents)
    file_path = str(get_file_path()).replace(DirPath.PROJECT.value, "")
    logger.error(msg=content, extra={'file_path': file_path})
    play_sound(FilePath.ERROR_MP3.value)


def custom_time(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("Asia/Tokyo")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()


conn = MySQL(database="tradingbot").conn
cur = conn.cursor()

content_size = 80
log_content = \
    "%(asctime)s :: %(levelname)-7s :: %(message)-{content_size}s %(file_path)s"\
    .format(content_size=content_size)

logger = getLogger(__name__)
logger.setLevel(DEBUG)

# create file handler
fh = FileHandler(FilePath.SYSTEM_LOG.value)
fh.setLevel(DEBUG)
fh.setFormatter(Formatter(log_content))

# create console handler
sh = StreamHandler()
sh.setLevel(DEBUG)
sh.setFormatter(Formatter(log_content))

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(sh)

Formatter.converter = custom_time
logger.propagate = False
