import random
import setup_logging
from Browser import Browser
import pandas as pd


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
