import webbrowser
import pandas as pd
import random
import json
from setup_logging import logger


class PlayList:

    def __init__(self, chrome_path: str):
        self.songs = pd.DataFrame()
        self.chrome_path = chrome_path
        self.SONG_NAME_COLUMN = 'Song_Name'
        self.SONG_URL_COLUMN = 'Song_URL'

    def read_from_bookmarks(self, bookmark_file_name: str):
        bookmarks_names_urls: dict = {}
        try:
            with open(bookmark_file_name, newline='') as file_handle:
                for linecount, line in enumerate(file_handle):
                    if linecount != 0 and 'youtube' in line:
                        if '<DT>' in line:
                            url_start_loc = line.find('A HREF="') + 8
                            url_end_loc = line.find('"', url_start_loc + 1)
                            url = line[url_start_loc:url_end_loc]
                            name_start_loc = line.find('">', url_end_loc) + 2
                            name_end_loc = line.find('</A>', name_start_loc)
                            name = line[name_start_loc:name_end_loc]
                            bookmarks_names_urls.update({name: url})
        except FileNotFoundError:
            logger.error("exception encountered when opening bookmark file and parsing the bookmarks")
        prepared_dict: dict = {
            song_key: song_value
            for song_key, song_value
            in enumerate(
                bookmarks_names_urls.items()
            )
        }
        self.songs = pd.DataFrame.from_dict(
            prepared_dict,
            orient="index",
            columns=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        logger.info(
            f"loaded {len(self.songs)} songs into a song list"
        )
        return self.songs

    def write_to_csv(self, csv_file_name: str):
        self.songs.to_csv(
            csv_file_name,
            columns=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN],
            index_label="Index"
        )
        logger.info(
            f"completed writing {len(self.songs)} songs "
            f"from song list into {csv_file_name}"
        )
        return True

    def read_from_excel(self, excel_file_name: str):
        self.songs = pd.read_excel(
            excel_file_name,
            usecols=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        logger.info(f"loaded {len(self.songs)} songs into the song list")
        return self.songs

    def read_from_csv(self, csv_file_name: str):
        self.songs = pd.read_csv(
            csv_file_name,
            header=0,
            names=[self.SONG_NAME_COLUMN, self.SONG_URL_COLUMN]
        )
        logger.info(f"loaded {len(self.songs)} songs into the song list")
        return self.songs

    def play_random(self):
        songlist_item_url: str = ''
        try:
            (songlist_item_name,
             songlist_item_url) = random.choice(self.songs.values.tolist())
            logger.info(f"opening {songlist_item_name} using {songlist_item_url}")
        except:
            logger.error(f"error opening songs to make a random choice")
        try:
            chrome_path: str = f'{self.chrome_path} %s'
            webbrowser.get(chrome_path).open(songlist_item_url, 2)
        except:
            logger.error("received an error when opening chrome to execute the song url")


if __name__ == '__main__':
    # good config.json will have all elements in config_template.json
    # except just the file type used will need a good value
    config_file_name: str = 'config.json'
    with open(config_file_name) as config_handle:
        configs: json = json.load(config_handle)
    logger.info(f"loaded program configurations from {config_file_name}")
    my_playlist: PlayList = PlayList(configs["chrome_path"])
    # save this for later!
    songs: pd.DataFrame = my_playlist.read_from_bookmarks(configs["bookmarks"])
    # songs = my_playlist.read_from_excel(configs["xlsx_file_name"])
    # print(songs)
    # csv_file_name = configs["csv_file_name"]
    # songs = read_from_csv(csv_file_name)
    songs.to_excel(configs["xlsx_file_name"], index_label="Index")
    # song_list = dict(songs.values.tolist())
    # save this for later
    # write_to_csv(csv_file_name, songs)
    my_playlist.play_random()
