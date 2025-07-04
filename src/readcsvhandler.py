import pandas as pd
from src.exceptions import EmptyPlaylistError
from src.readhandler import ReadHandler
from playlist_shared_utils import check_file_type


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
        except pd.errors.ParserError:
            self.raise_and_log(
                pd.errors.ParserError,
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
