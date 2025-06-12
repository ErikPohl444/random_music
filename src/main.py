import webbrowser
import pandas as pd
import random
import json     
import setup_logging
import os
from setup_logging import logger
import argparse


# Using standardized comments here even though the code is self documenting
# 1. to show what it looks like [I can always reduce comments later]
# 2. evaluate the maintenance requirements
# 3. Use this as an object lesson to define guidelines around

# in terms of look before you leap [lbyl] and easier to ask forgiveness than permission [eafp], i've tried both
# i approached python first with lybl from other language, moved to a kind of extreme eafp, and
# am playing here and in future scripting changes to find a good balance.


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

    def read_from_bookmarks(self, bookmark_file_name: str) -> pd.DataFrame:
        """Reads YouTube song links from a Chrome bookmarks file in dataframe

        Args:
            bookmark_file_name (str): Path to the bookmarks file.

        Returns:
            pd.DataFrame: DataFrame containing song names and URLs.
        """

        # build a formatted dictionary of song urls and names
        bookmarks_names_urls = self._read_youtube_links(bookmark_file_name)
        # convert dict to dataframe
        self.songs = pd.DataFrame.from_dict(
            bookmarks_names_urls,
            orient="index",
            columns=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        self.logger.info(
            f"loaded {len(self.songs)} songs into a song list"
        )
        return self.songs

    def write_to_csv(self, song_file_name: str) -> bool:
        """Write a playlist to a csv file.

        Args:
            song_file_name (str): The name of the song data file.

        Returns:
            boolean: Success flag for the write operation.
        """
        check_file_type(song_file_name, ['.csv'])
        self.songs.to_csv(
            song_file_name,
            columns=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN],
            index_label="Index"
        )
        self.logger.info(
            f"completed writing {len(self.songs)} songs "
            f"from song list into {song_file_name}"
        )
        return True

    def read_from_excel(self, song_file_name: str) -> pd.DataFrame:
        """Reads a song data into a playlist.

        Args:
            song_file_name (str): The name of the song data file.

        Returns:
            dataframe: A dataframe containing all of the song data from the file.
        """
        check_file_type(song_file_name, ['.xlsx'])
        self.songs = pd.read_excel(
            song_file_name,
            usecols=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        self.logger.info(f"loaded {len(self.songs)} songs into the song list")
        return self.songs

    def read_from_csv(self, song_file_name: str) -> pd.DataFrame:
        """Reads a song data into a playlist from a csv file.

        Args:
            song_file_name (str): The name of the song data file.

        Returns:
            dataframe: A dataframe containing all of the song data from the file.
        """
        check_file_type(song_file_name, ['.csv'])
        try:
            self.songs = pd.read_csv(
                song_file_name,
                header=0,
                names=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
            )
            self.logger.info(f"loaded {len(self.songs)} songs into the song list")
        except FileNotFoundError:
            self.logger.error(f"file {song_file_name} does not exist to load.")
            exit(1)
        return self.songs

    def play_random(self) -> bool:
        """Plays a random song from the playlist's song list.

        Args:
            No parameters

        Returns:
            bool: True for success.
        """
        songlist_item_url = ''
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
    parser = argparse.ArgumentParser(description="Example program")
    # Add arguments
    parser.add_argument(
        "-write_to_xlsx",
        "--wx",
        type=str,
        nargs='?',
        help="xlsx file name to write to",
        default="write_playlist.xlsx"
    )
    parser.add_argument(
        "-write_to_csv",
        "--wc",
        type=str,
        nargs='?',
        help="csv file name to write to",
        default="write_playlist.csv"
    )
    parser.add_argument(
        "-rb",
        "--read_from_bookmarks",
        type=str,
        nargs='?',
        default=configs["bookmarks"],
        help='bookmarks file name to read from'
    )
    parser.add_argument(
        "-rc",
        "--read_from_csv",
        type=str,
        nargs='?',
        default=configs["csv_file_name"],
        help='csv file name to read from'
    )
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
    my_playlist = PlayList(chrome_browser, logger)
    if args.read_from_bookmarks:
        songs: pd.DataFrame = my_playlist.read_from_bookmarks(args.read_from_bookmarks)
    # if args.read_from_csv:
    #    songs = my_playlist.read_from_csv(args.read_from_csv)
    if songs.bool:
        if args.wx:
            songs.to_excel(configs["xlsx_file_name"], index_label="Index")
        # if args.write_to_csv:
        #     my_playlist.write_to_csv(args.write_to_csv, songs)
        my_playlist.play_random()


if __name__ == '__main__':
    execute_random_song_selection()
