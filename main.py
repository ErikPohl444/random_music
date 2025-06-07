import webbrowser
import pandas as pd
import random
import json     
import setup_logging
import os
from setup_logging import logger

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
        print(self.browser_executable_path, url)
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

    def read_from_bookmarks(self, bookmark_file_name: str) -> pd.DataFrame:
        """Reads YouTube song links from a Chrome bookmarks file.

        Args:
            bookmark_file_name (str): Path to the bookmarks file.

        Returns:
            pd.DataFrame: DataFrame containing song names and URLs.
        """
        bookmarks_names_urls: dict = {}
        try:
            with open(bookmark_file_name, newline='') as file_handle:
                for linecount, line in enumerate(file_handle):
                    if linecount != 0 and 'youtube' in line:
                        if '<DT>' in line:
                            url_start_loc: int = line.find('A HREF="') + 8
                            url_end_loc: int = line.find('"', url_start_loc + 1)
                            url: str = line[url_start_loc:url_end_loc]
                            name_start_loc: int = line.find('">', url_end_loc) + 2
                            name_end_loc: int = line.find('</A>', name_start_loc)
                            name: str = line[name_start_loc:name_end_loc]
                            bookmarks_names_urls.update({name: url})
        except FileNotFoundError as e:
            self.logger.error(f"exception encountered when opening bookmark file and parsing the bookmarks: {e}")
        formatted_song_info: dict = {
            song_key: song_value
            for song_key, song_value
            in enumerate(
                bookmarks_names_urls.items()
            )
        }
        self.songs = pd.DataFrame.from_dict(
            formatted_song_info,
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
    my_playlist = PlayList(chrome_browser, logger)
    # save this for later!
    songs: pd.DataFrame = my_playlist.read_from_bookmarks(configs["bookmarks"])
    # songs = my_playlist.read_from_excel(configs["xlsx_file_name"])
    # print(songs)
    # csv_file_name = configs["csv_file_name"]
    # songs = read_from_csv(csv_file_name)
    songs.to_excel(configs["xlsx_file_name"], index_label="Index")
    # song_list = dict(songs.values.tolist())
    # save this for later
    # write_to_csv(csv_file_name, songs)
    my_playlist.play_random()


if __name__ == '__main__':
    execute_random_song_selection()
