import pytest
import pandas as pd
import types
import os
from unittest import mock
from src.main import (
    Browser, check_file_type, PlayList, read_config_file
)

class DummyLogger:
    def __init__(self):
        self.logs = []
    def info(self, msg): self.logs.append(msg)
    def error(self, msg): self.logs.append(msg)

@pytest.fixture
def dummy_logger():
    return DummyLogger()

@pytest.fixture
def browser(dummy_logger):
    # Use 'chrome' as dummy browser_executable_path
    return Browser('chrome', dummy_logger)

@pytest.fixture
def playlist(browser, dummy_logger):
    return PlayList(browser, dummy_logger)

def test_check_file_type_accepts_valid():
    assert check_file_type("test.csv", [".csv"])
    assert check_file_type("test.CSV", [".csv"])
    assert check_file_type("test.xlsx", [".xlsx"])
    assert check_file_type("test.json", [".json"])

def test_check_file_type_rejects_invalid():
    with pytest.raises(ValueError):
        check_file_type("test.txt", [".csv"])
    with pytest.raises(ValueError):
        check_file_type("test.xls", [".csv", ".xlsx"])

def test_browser_open_browser_with_url_success(monkeypatch, dummy_logger):
    called = {}
    class DummyBrowser:
        def open(self, url, n):
            called['url'] = url
            return True
    monkeypatch.setattr("webbrowser.get", lambda path: DummyBrowser())
    b = Browser("dummy_path", dummy_logger)
    b.open_browser_with_url("http://example.com")
    assert called['url'] == "http://example.com"

def test_browser_open_browser_with_url_error(monkeypatch, dummy_logger):
    def raise_error(path):
        class Dummy:
            def open(self, url, n): raise Exception("fail")
        return Dummy()
    monkeypatch.setattr("webbrowser.get", raise_error)
    b = Browser("dummy_path", dummy_logger)
    # The logger.info should be called due to exception
    b.open_browser_with_url("http://example.com")
    assert any("issue opening web browser" in log for log in dummy_logger.logs)

def test_playlist_split_a_href():
    html = '<DT><A HREF="https://youtube.com/test">Song Name</A>'
    result = PlayList._split_a_href(html)
    assert result == ["Song Name", "https://youtube.com/test"]

def test_playlist_read_youtube_links(tmp_path, playlist):
    content = '<DT><A HREF="https://youtube.com/1">Song1</A>\n' \
              '<DT><A HREF="https://youtube.com/2">Song2</A>\n'
    file = tmp_path / "bookmarks.html"
    file.write_text("header\n" + content)
    result = playlist._read_youtube_links(str(file))
    assert isinstance(result, dict)
    assert any("Song1" in v[0] for v in result.values())

def test_playlist_read_youtube_links_file_not_found(playlist, dummy_logger):
    result = playlist._read
