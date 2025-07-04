from src.read_handlers.readhandler import ReadHandler
import pandas as pd
from src.exceptions import EmptyPlaylistError
from playlist_shared_utils import check_file_type


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
        except pd.errors.ParserError:
            self.raise_and_log(
                pd.errors.ParserError,
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
