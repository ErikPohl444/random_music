import pandas as pd
import json
import os
import setup_logging
from setup_logging import logger
import argparse
import sqlite3
from playlist_read_handlers import ReadBookmarksHandler, ReadExcelHandler, ReadCSVHandler
from playlist_write_handlers import CSVWriteHandler, ExcelWriteHandler
from Browser import Browser
from Playlist import PlayList

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
        bool: connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Optional, for dict-like row access
    return conn


def check_file_type(file_name: str, file_exts: list[str]) -> bool:
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in file_exts:
        if len(file_exts) == 1:
            raise ValueError(f"Invalid file type: {ext}. Allowed type is {file_exts}")
        else:
            raise ValueError(f"Invalid file type: {ext}. Allowed types are {file_exts}")
    return True


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


def execute_random_song_selection():
    """Reads configurations and, based on the configurations, loads a list of song data, selecting one to play.

    Args:
        No parameters

    Returns:
        None
    """

    # good config.json will have all elements in config_template.json
    # except just the file type used will need a good value
    configs: json = read_config_file()
    chrome_browser = Browser(configs["chrome_path"] + " %s", logger)
    # read cli arguments
    args = get_args(configs)
    # get db connection
    db_conn = get_db_connection(configs["db_path"])

    my_playlist = PlayList(chrome_browser, logger)
    if args.read_from_bookmarks:
        my_playlist.read_songlist_handler = ReadBookmarksHandler(logger)
    # if args.read_from_csv:
    #     my_playlist.read_songlist_handler = ReadCSVHandler(logger)
    songs: pd.DataFrame = my_playlist.read_songs(args.read_from_bookmarks)
    if songs.bool:
        if args.wx:
            my_playlist.write_songlist_handler = ExcelWriteHandler
            my_playlist.write_songlist_handler.write_songlist(songs, configs["xlsx_file_name"])
        # if args.wc:
        #     my_playlist.write_songlist_handler = CSVWriteHandler
        #     my_playlist.write_songlist_handler.write_songlist(songs, configs["csv_file_name"])
        my_playlist.play_random()
    db_conn.close()


if __name__ == '__main__':
    execute_random_song_selection()
