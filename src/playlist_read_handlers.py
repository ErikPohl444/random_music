from abc import ABC, abstractmethod

import pandas.errors
from html.parser import HTMLParser

from setup_logging import logger
import pandas as pd
from playlist_shared_utils import check_file_type
from src.exceptions import PlaylistError, EmptyPlaylistError


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_anchor = False
        self.link_text = ""
        self.last_link_text = ""
        self.last_url = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.in_anchor = True
            self.link_text = ""
            for name, value in attrs:
                if name == "href":
                    self.current_link = value

    def handle_data(self, data):
        if self.in_anchor:
            self.link_text += data

    def handle_endtag(self, tag):
        if tag == "a" and self.in_anchor:
            self.last_url = self.current_link
            self.last_link_text = self.link_text.strip()
            self.in_anchor = False
            self.current_link = None
            self.link_text = ""


class ReadHandler(ABC):
    SONG_NAME_COLUMN = 'Song_Name'
    SONG_URL_COLUMN = 'Song_URL'

    def __init__(self, read_handler_logger: logger):
        self.logger = read_handler_logger

    def raise_and_log(self, logged_exception: Exception, exception_message: str):
        self.logger.error(exception_message)
        raise logged_exception(exception_message)

    @abstractmethod
    def get_songlist(self, source: str):
        pass


class ReadBookmarksHandler(ReadHandler):

    def _split_a_href(self, html_line: str) -> [str, str]:
        """Removes the link name and link url from a line of html containing an "a href"

        Args:
            html_line (str): Line of html

        Returns:
            List of two strings representing the name and then the url
        """

        parser = MyHTMLParser()
        parser.feed(html_line)
        if not parser.last_link_text or not parser.last_url:
            self.raise_and_log(
                PlaylistError,
                f"HTML LINE {html_line} doesn't contain enough information to divide into link and text"
            )
        return parser.last_link_text, parser.last_url

    def _interesting_html_line(self, html_line: str) -> bool:
        return 'youtube' in html_line and '<DT>' in html_line

    def _read_youtube_links(self, bookmark_file_name: str) -> dict:
        """Reads a flat file containing a bookmarks export from Chrome and extracts the youtube links

        Args:
            bookmark_file_name (str): Path to the bookmarks file.

        Returns:
            dict: A Dict containing all youtube link name and urls
        """
        bookmarks_names_urls: dict = {}
        songlist_index = 0
        try:
            with open(bookmark_file_name, newline='') as file_handle:
                for linecount, line in enumerate(file_handle):
                    if linecount != 0:
                        if self._interesting_html_line(line):
                            bookmarks_names_urls.update({songlist_index: self._split_a_href(line)})
                            songlist_index += 1
        except FileNotFoundError as e:
            self.raise_and_log(
                FileNotFoundError,
                f"Playlist file {bookmark_file_name} does not exist to load songs from: {e}"
            )
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
        if songs.empty:
            self.raise_and_log(EmptyPlaylistError, "There were no songs found in the playlist source")
        self.logger.info(
            f"loaded {len(songs)} songs into a song list"
        )
        return songs


class ReadCSVHandler(ReadHandler):

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
            self.raise_and_log(FileNotFoundError, f"Playlist file {source} does not exist to load songs from.")
        except pandas.errors.ParserError:
            self.raise_and_log(
                pandas.errors.ParserError,
                f"Check the format of playlist file {source}.  It is not parsing as a csv.")
        except UnicodeDecodeError:
            self.raise_and_log(
                UnicodeDecodeError,
                f"Check the encoding of playlist file {source}.  It is not parsing as a UTF-8.")
        except ValueError:
            self.raise_and_log(
                ValueError,
                f"Check the headers and fields of playlist file {source}. "
                f"One or more fields contains invalid values."
            )
        if songs.empty:
            self.raise_and_log(EmptyPlaylistError, f"Playlist file {source} contained no songs.")
        self.logger.info(f"loaded {len(songs)} songs into the song list")
        return songs


class ReadExcelHandler(ReadHandler):

    def get_songlist(self, source: str) -> pd.DataFrame:
        """Reads a song data into a playlist.

        Args:
            source (str): The name of the song data file. song_file_name

        Returns:
            dataframe: A dataframe containing all of the song data from the file.
        """
        check_file_type(source, ['.xlsx'])
        try:
            songs = pd.read_excel(
                source,
                usecols=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
            )
        except FileNotFoundError:
            self.raise_and_log(FileNotFoundError, f"Playlist file {source} does not exist to load songs from.")
        except pandas.errors.ParserError:
            self.raise_and_log(
                pandas.errors.ParserError,
                f"Check the format of playlist file {source}.  It is not parsing as an excel.")
        except ValueError:
            self.raise_and_log(
                ValueError,
                f"Check the headers and fields of playlist file {source}. "
                f"One or more fields contains invalid values.")
        if songs.empty:
            self.raise_and_log(EmptyPlaylistError, "Playlist source contains no songs")
        self.logger.info(f"loaded {len(songs)} songs into the song list")
        return songs
