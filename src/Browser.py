import setup_logging
from setup_logging import logger
import webbrowser


class Browser:
    """Provides an interface for calling browsers by their executable to open a URL window .

    Attributes:
        browser_executable_path (str): Path to the browser executable.
        browser_logger (Logger): Logger instance for logging events.
    """

    def __init__(self, browser_executable_path: str, browser_logger: logger):
        self.browser_executable_path = browser_executable_path
        self.browser_logger = browser_logger

    def open_browser_with_url(self, url: str):
        """Opens the browser to load the given URL.

        Args:
            url (str): The url to open using the browser.

        Returns:
            None
        """
        self.browser_logger.info(self.browser_executable_path, url)
        try:
            webbrowser.get(self.browser_executable_path).open(url, 2)
        except webbrowser.Error as e:
            self.browser_logger.info(f"issue opening web browser with this url: {e}")
