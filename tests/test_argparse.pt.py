import sys
import pytest
from src.main import get_args


def test_get_args_defaults(monkeypatch):
    configs = {
        "bookmarks": "default_bookmarks.html",
        "csv_file_name": "default_playlist.csv",
        "xlsx_file_name": "default_playlist.xlsx"
    }
    monkeypatch.setattr(sys, "argv", ["main.py"])
    args = get_args(configs)
    assert args.wx == "write_playlist.xlsx"
    assert args.wc == "write_playlist.csv"
    assert args.read_from_bookmarks == configs["bookmarks"]
    assert args.read_from_csv == configs["csv_file_name"]


def test_get_args_overrides(monkeypatch):
    configs = {
        "bookmarks": "default_bookmarks.html",
        "csv_file_name": "default_playlist.csv",
        "xlsx_file_name": "default_playlist.xlsx"
    }
    monkeypatch.setattr(
        sys, "argv",
        [
            "main.py",
            "--wx", "custom.xlsx",
            "--wc", "custom.csv",
            "--read_from_bookmarks", "bm.html",
            "--read_from_csv", "songs.csv"
        ]
    )
    args = get_args(configs)
    assert args.wx == "custom.xlsx"
    assert args.wc == "custom.csv"
    assert args.read_from_bookmarks == "bm.html"
    assert args.read_from_csv == "songs.csv"


def test_get_args_partial(monkeypatch):
    configs = {
        "bookmarks": "default_bookmarks.html",
        "csv_file_name": "default_playlist.csv",
        "xlsx_file_name": "default_playlist.xlsx"
    }
    monkeypatch.setattr(
        sys, "argv",
        [
            "main.py",
            "--wx", "special.xlsx"
        ]
    )
    args = get_args(configs)
    assert args.wx == "special.xlsx"
    assert args.wc == "write_playlist.csv"
    assert args.read_from_bookmarks == configs["bookmarks"]
    assert args.read_from_csv == configs["csv_file_name"]


def test_get_args_help(monkeypatch):
    configs = {
        "bookmarks": "bm.html",
        "csv_file_name": "songs.csv",
        "xlsx_file_name": "songs.xlsx"
    }
    monkeypatch.setattr(sys, "argv", ["main.py", "--help"])
    with pytest.raises(SystemExit):
        get_args(configs)
