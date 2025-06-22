from abc import ABC, abstractmethod
import os
from setup_logging import logger


def check_file_type(file_name: str, file_exts: list[str]) -> bool:
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in file_exts:
        if len(file_exts) == 1:
            raise ValueError(f"Invalid file type: {ext}. Allowed type is {file_exts}")
        else:
            raise ValueError(f"Invalid file type: {ext}. Allowed types are {file_exts}")
    return True


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
