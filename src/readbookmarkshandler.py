import pandas as pd
from src.exceptions import EmptyPlaylistError, PlaylistError
from src.readhandler import ReadHandler
from setup_logging import logger
from src.myhtmlparser import MyHTMLParser


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
