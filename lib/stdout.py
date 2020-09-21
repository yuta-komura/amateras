from lib.config import FilePath


def amateras():
    path = FilePath.AA.value
    with open(path) as f:
        print(f.read())
