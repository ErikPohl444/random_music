import pandas as pd
import json
from setup_logging import logger
import argparse
import sqlite3
from src.read_handlers.readhandler import ReadHandler
from src.read_handlers.readcsvhandler import ReadCSVHandler
from src.read_handlers.readbookmarkshandler import ReadBookmarksHandler
from playlist_write_handlers import CSVWriteHandler, ExcelWriteHandler, WriteHandler
from Browser import Browser
from playlist import PlayList
from playlist_shared_utils import check_file_type

# i went class happy here.  kinda demonstrates how even clean coding using a design pattern can contribute
# to difficulty reading code.  glad to denormalize it at some point in the future, but will leave as-is for now.

# Using standardized comments here even though the code is self documenting
# 1. to show what it looks like [I can always reduce comments later]
# 2. evaluate the maintenance requirements
# 3. Use this as an object lesson to define guidelines around

# in terms of look before you leap [lbyl] and easier to ask forgiveness than permission [eafp], i've tried both
# i approached python first with lybl from other language, moved to a kind of extreme eafp, and
# am playing here and in future scripting changes to find a good balance.


def get_db_connection(db_path: str) -> sqlite3.connect:
    """opens a sqlite3 connection.

    Args:
        db_path: str: path to database

    Returns:
        sqlite3.connect: connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Optional, for dict-like row access
    return conn


def read_config_file(config_file_name: str = "./config.json") -> json:
    """Loads configuration from a JSON file.

    Args:
        config_file_name (str): The name of the json configuration file.

    Returns:
        dict: Dictionary with configuration settings.
    """
    check_file_type(config_file_name, ['.json'])
    try:
        with open(config_file_name) as config_handle:
            loaded_configs: json = json.load(config_handle)
        logger.info(f"loaded program configurations from {config_file_name}")
    except FileNotFoundError as e:
        logger.info(f'configuration file not found at {config_file_name} producing error {e}')
    return loaded_configs


def get_args(configs: dict):
    """Set up arg parser with arguments and return parsed values.

    Args:
        configs (dict): Configurations loaded from the config file

    Returns:
        parsed arguments
    """
    parser = argparse.ArgumentParser(description="Random music")
    arg_specs = [
        {
            "flags": ["-write_to_xlsx", "--wx"],
            "kwargs": {
                "type": str,
                "nargs": '?',
                "help": "xlsx file name to write to",
                "default": configs.get("xlsx_file_name", "write_playlist.xlsx"),
            }
        },
        {
            "flags": ["-write_to_csv", "--wc"],
            "kwargs": {
                "type": str,
                "nargs": '?',
                "help": "csv file name to write to",
                "default": configs.get("csv_file_name", "write_playlist.csv"),
            }
        },
        {
            "flags": ["-rb", "--read_from_bookmarks"],
            "kwargs": {
                "type": str,
                "nargs": '?',
                "help": 'bookmarks file name to read from',
                "default": configs.get("bookmarks", "default_bookmarks.html"),
            }
        },
        {
            "flags": ["-rc", "--read_from_csv"],
            "kwargs": {
                "type": str,
                "nargs": '?',
                "help": 'csv file name to read from',
                "default": configs.get("csv_file_name", "default_playlist.csv"),
            }
        }
    ]
    for spec in arg_specs:
        parser.add_argument(*spec["flags"], **spec["kwargs"])
    return parser.parse_args()


def select_read_songlist_handler(args: argparse.Namespace) -> ReadHandler:
    """Choose a read handler

    Args:
        args: dict: arguments passed to program
    Returns:
        ReadHandler
    """
    if args.read_from_bookmarks:
        return ReadBookmarksHandler(logger, args.read_from_bookmarks)
    elif args.read_from_csv:
        return ReadCSVHandler(logger, None)
    raise ValueError("No read handler identified by cli arguments")


def select_write_songlist_handler(args: argparse.Namespace, configs: dict) -> WriteHandler:
    """Choose a write handler and set the write file name based on args and configs

    Args:
        args: dict: arguments passed to program
        configs: dict: configs loaded at runtime
    Returns:
        WriteHandler
    """
    if args.wx:
        return ExcelWriteHandler(configs["xlsx_file_name"])
    elif args.wc:
        return CSVWriteHandler(configs["csv_file_name"])
    raise ValueError("No write handler identified by cli arguments")



def execute_random_song_selection():
    """Reads configurations and, based on the configurations, loads a list of song data, selecting one to play.

    Args:
        No parameters

    Returns:
        None
    """

    configs: json = read_config_file()
    chrome_browser = Browser(configs["chrome_path"] + " %s", logger)
    args = get_args(configs)
    db_conn = get_db_connection(configs["db_path"])
    my_playlist = PlayList(chrome_browser, logger)
    my_playlist.read_songlist_handler = select_read_songlist_handler(args)
    my_playlist.read_songs()
    if my_playlist.songs.bool:
        my_playlist.write_songlist_handler = select_write_songlist_handler(args, configs)
        if my_playlist.write_songlist_handler:
            my_playlist.write_songlist_handler.write_songlist(my_playlist.songs)
        my_playlist.play_random()
    db_conn.close()


if __name__ == '__main__':
    execute_random_song_selection()
