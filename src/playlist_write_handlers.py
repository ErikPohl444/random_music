from abc import ABC, abstractmethod
from src.setup_logging import logger, raise_and_log
from playlist_shared_utils import check_file_type


class WriteHandler(ABC):
    SONG_NAME_COLUMN = 'Song_Name'
    SONG_URL_COLUMN = 'Song_URL'

    def __init__(self, file_name: str):
        self._write_file_name = file_name

    @abstractmethod
    def write_songlist(self, songs):
        pass


class ExcelWriteHandler(WriteHandler):

    def write_songlist(self, songs):
        try:
            songs.to_excel(self._write_file_name, index_label="Index")
        except IOError:
            raise_and_log(IOError, f"Error writing {self._write_file_name}")
        logger.info(
            f"completed writing {len(songs)} songs "
            f"from song list into {self._write_file_name}"
        )


class CSVWriteHandler(WriteHandler):

    def write_songlist(self, songs):
        """Write a playlist to a csv file.

                Args:
                    songs (str):songs to write to excel

                Returns:
                    boolean: Success flag for the write operation.
                """
        check_file_type(self._write_file_name, ['.csv'])
        try:
            songs.to_csv(
                self._write_file_name,
                columns=[CSVWriteHandler.SONG_NAME_COLUMN, CSVWriteHandler.SONG_URL_COLUMN],
                index_label="Index"
            )
        except IOError:
            raise_and_log(IOError, f"Error writing {self._write_file_name}")
        logger.info(
            f"completed writing {len(songs)} songs "
            f"from song list into {self._write_file_name}"
        )
        return True
