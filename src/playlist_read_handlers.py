from abc import ABC, abstractmethod

import pandas.errors

from setup_logging import logger
import pandas as pd
from playlist_shared_utils import check_file_type
from src.exceptions import EmptyPlaylistError


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
        if not songs:
            raise EmptyPlaylistError
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
        except FileNotFoundError:
            improved_message = f"Playlist file {source} does not exist to load songs from."
            self.logger.error(improved_message)
            raise FileNotFoundError(improved_message)
        except pandas.errors.ParserError:
            improved_message = f"Check the format of playlist file {source}.  It is not parsing as a csv."
            self.logger.error(improved_message)
            raise FileNotFoundError(improved_message)
        except UnicodeDecodeError:
            improved_message = f"Check the encoding of playlist file {source}.  It is not parsing as a UTF-8."
            self.logger.error(improved_message)
            raise FileNotFoundError(improved_message)
        except ValueError:
            improved_message = f"Check the headers and fields of playlist file {source}.  One or more fields contains invalid values."
            self.logger.error(improved_message)
            raise FileNotFoundError(improved_message)
        if not songs:
            improved_message = f"Playlist file {source} contained no songs."
            self.logger.error(improved_message)
            raise EmptyPlaylistError(improved_message)
        self.logger.info(f"loaded {len(songs)} songs into the song list")
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
        if not songs:
            raise EmptyPlaylistError
        self.read_logger.info(f"loaded {len(songs)} songs into the song list")
        return songs
