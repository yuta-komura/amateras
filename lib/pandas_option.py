import pandas as pd


def display_max_columns():
    pd.options.display.max_columns = None


def display_max_rows():
    pd.options.display.max_rows = None


def display_round_down():
    pd.options.display.float_format = '{:.2f}'.format
