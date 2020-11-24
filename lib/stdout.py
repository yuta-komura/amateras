from lib.config import FilePath


def AA():
    path = FilePath.AA.value
    with open(path) as f:
        print(f.read())
