import webbrowser
import pandas as pd
import random
import json     
import setup_logging
import os
from setup_logging import logger
from abc import ABC, abstractmethod
import argparse
import sqlite3

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


class Browser:
    """Provides an interface for calling browsers by their executable to open a URL window .

    Attributes:
        browser_executable_path (str): Path to the browser executable.
        browser_logger (Logger): Logger instance for logging events.
    """

    def __init__(self, browser_executable_path: str, browser_logger: logger):
        self.browser_executable_path = browser_executable_path
        self.browser_logger = browser_logger

    def open_browser_with_url(self, url: str):
        """Opens the browser to load the given URL.

        Args:
            url (str): The url to open using the browser.

        Returns:
            None
        """
        self.browser_logger.info(self.browser_executable_path, url)
        try:
            webbrowser.get(self.browser_executable_path).open(url, 2)
        except webbrowser.Error as e:
            self.browser_logger.info(f"issue opening web browser with this url: {e}")


def check_file_type(file_name: str, file_exts: list[str]) -> bool:
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in file_exts:
        if len(file_exts) == 1:
            raise ValueError(f"Invalid file type: {ext}. Allowed type is {file_exts}")
        else:
            raise ValueError(f"Invalid file type: {ext}. Allowed types are {file_exts}")
    return True


class ReadHandler(ABC):
    SONG_NAME_COLUMN = 'Song_Name'
    SONG_URL_COLUMN = 'Song_URL'

    @abstractmethod
    def get_songlist(self, source: str):
        pass


class ReadBookmarksHandler(ReadHandler):

    def __init__(self, read_logger):
        self.logger = read_logger

    @staticmethod
    def _split_a_href(html_line: str) -> [str, str]:
        """Removes the link name and link url from a line of html containing an "a href"

        Args:
            html_line (str): Line of html

        Returns:
            List of two strings representing the name and then the url
        """
        url_start_loc: int = html_line.find('A HREF="') + 8
        url_end_loc: int = html_line.find('"', url_start_loc + 1)
        url: str = html_line[url_start_loc:url_end_loc]
        name_start_loc: int = html_line.find('">', url_end_loc) + 2
        name_end_loc: int = html_line.find('</A>', name_start_loc)
        name: str = html_line[name_start_loc:name_end_loc]
        return [name, url]

    def _read_youtube_links(self, bookmark_file_name: str) -> dict:
        """Reads a flat file containing a bookmarks export from Chrome and extracts the youtube links

        Args:
            bookmark_file_name (str): Path to the bookmarks file.

        Returns:
            dict: A Dict containing all youtube link name and urls
        """
        bookmarks_names_urls: dict = {}
        key = 0
        try:
            with open(bookmark_file_name, newline='') as file_handle:
                for linecount, line in enumerate(file_handle):
                    if linecount != 0 and 'youtube' in line and '<DT>' in line:
                        name, url = self._split_a_href(line)
                        bookmarks_names_urls.update({key: (name, url)})
                        key += 1
        except FileNotFoundError as e:
            self.logger.error(f"exception encountered when opening bookmark file and parsing the bookmarks: {e}")
        return bookmarks_names_urls

    def get_songlist(self, source: str) -> pd.DataFrame:
        """Reads YouTube song links from a Chrome bookmarks file in dataframe

        Args:
            source (str): Path to the bookmarks file, bookmark_file_name

        Returns:
            pd.DataFrame: DataFrame containing song names and URLs.
        """

        # build a formatted dictionary of song urls and names
        logger.info('in bookmark read songlist')
        bookmarks_names_urls = self._read_youtube_links(source)

        # convert dict to dataframe
        songs = pd.DataFrame.from_dict(
            bookmarks_names_urls,
            orient="index",
            columns=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        self.logger.info(
            f"loaded {len(songs)} songs into a song list"
        )
        return songs


class ReadCSVHandler(ReadHandler):

    def __init__(self, read_logger):
        self.logger = read_logger

    def get_songlist(self, source: str) -> pd.DataFrame:
        """Reads a song data into a playlist from a csv file.

        Args:
            source (str): The name of the song data file. song_file_name

        Returns:
            dataframe: A dataframe containing all of the song data from the file.
        """
        check_file_type(source, ['.csv'])
        try:
            songs = pd.read_csv(
                source,
                header=0,
                names=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
            )
            self.logger.info(f"loaded {len(songs)} songs into the song list")
        except FileNotFoundError:
            self.logger.error(f"file {source} does not exist to load.")
            exit(1)
        return songs


class ReadExcelHandler(ReadHandler):

    def __init__(self, read_logger):
        self.logger = read_logger

    def get_songlist(self, source: str) -> pd.DataFrame:
        """Reads a song data into a playlist.

        Args:
            source (str): The name of the song data file. song_file_name

        Returns:
            dataframe: A dataframe containing all of the song data from the file.
        """
        check_file_type(source, ['.xlsx'])
        songs = pd.read_excel(
            source,
            usecols=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        self.read_logger.info(f"loaded {len(songs)} songs into the song list")
        return songs


class WriteHandler(ABC):
    SONG_NAME_COLUMN = 'Song_Name'
    SONG_URL_COLUMN = 'Song_URL'

    @abstractmethod
    def write_songlist(self, songs, destination: str):
        pass


class ExcelWriteHandler(WriteHandler):

    @staticmethod
    def write_songlist(songs, destination: str):
        songs.to_excel(destination, index_label="Index")


class CSVWriteHandler(WriteHandler):

    @staticmethod
    def write_songlist(songs, destination: str):
        """Write a playlist to a csv file.

                Args:
                    songs (str):songs to write to excel
                    destination (str): The name of the song data file.song_file_name
                    song_name_column (str): column header for song name
                    song_url_column (str): column header for song url

                Returns:
                    boolean: Success flag for the write operation.
                """
        check_file_type(destination, ['.csv'])
        songs.to_csv(
            destination,
            columns=[CSVWriteHandler.song_name_column, CSVWriteHandler.song_url_column],
            index_label="Index"
        )
        logger.info(
            f"completed writing {len(songs)} songs "
            f"from song list into {destination}"
        )
        return True


class PlayList:
    """Handles playlist operations for random music selection.

    Attributes:
        songs (dataframe): List of songs in a playlist.
        browser (Browser): Browser instance for opening songs.
        logger (Logger): Logger instance for logging events.
        SONG_NAME_COLUMN (str): Name of the song column.
        SONG_URL_COLUMN (str): Name of the URL column.
    """

    def __init__(self, browser: Browser, playlist_logger: setup_logging.logger):
        self.songs = pd.DataFrame()
        self.browser = browser
        self.logger = playlist_logger
        self.SONG_NAME_COLUMN = 'Song_Name'
        self.SONG_URL_COLUMN = 'Song_URL'
        self.read_songlist_handler = None
        self.write_songlist_handler = None

    def read_songs(self, source: str):
        if self.read_songlist_handler:
            self.songs = self.read_songlist_handler.get_songlist(source)
        return self.songs

    def play_random(self) -> bool:
        """Plays a random song from the playlist's song list.

        Args:
            No parameters

        Returns:
            bool: True for success.
        """
        try:
            (songlist_item_name,
             songlist_item_url) = random.choice(
                self.songs.values.tolist()
            )
            self.logger.info(f"opening {songlist_item_name} using {songlist_item_url}")
        except TypeError as e:
            self.logger.error(f"error opening songs to make a random choice: {e}")
            exit(1)
        self.browser.open_browser_with_url(songlist_item_url)
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
