from abc import ABC, abstractmethod
from src.setup_logging import logger


class ReadHandler(ABC):
    SONG_NAME_COLUMN = 'Song_Name'
    SONG_URL_COLUMN = 'Song_URL'

    def __init__(self, read_handler_logger: logger, source_file_name: str):
        self.logger = read_handler_logger
        self.read_file_name = source_file_name

    @abstractmethod
    def get_songlist(self, source: str):
        pass
