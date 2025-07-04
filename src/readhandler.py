from abc import ABC, abstractmethod
from setup_logging import logger


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
