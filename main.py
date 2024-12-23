import webbrowser
import pandas as pd
import random
import json
from setup_logging import logger


def read_from_bookmarks(bookmark_file):
    bookmarks_names_urls = {}
    with open(bookmark_file, newline='') as file_handle:
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
    prepared_dict = {
        song_key: song_value
        for song_key, song_value
        in enumerate(
            bookmarks_names_urls.items()
        )
    }
    bookmarks_names_urls = pd.DataFrame.from_dict(
        prepared_dict,
        orient="index",
        columns=['Song_Name', 'Song_URL']
    )
    logger.info(f"loaded {len(bookmarks_names_urls)} songs into a song list")
    return bookmarks_names_urls


def write_to_csv(csv_file_name, song_list):
    song_list.to_csv(
        csv_file_name,
        columns=['Song_Name', 'Song_URL'],
        index_label="Index"
    )
    logger.info(
        f"completed writing {len(song_list)} songs "
        f"from song list into {csv_file_name}"
    )
    return True


def read_from_excel(excel_file_name):
    songs = pd.read_excel(excel_file_name, usecols=["Song_Name", "Song_URL"])
    logger.info(f"loaded {len(songs)} songs into the song list")
    return songs


def read_from_csv(csv_file_name):
    song_list = pd.read_csv(
        csv_file_name,
        header=0,
        names=['Song_Name', 'Song_URL']
    )
    logger.info(f"loaded {len(song_list)} songs into the song list")
    return song_list


if __name__ == '__main__':
    with open("config.json") as config_handle:
        configs = json.load(config_handle)
    logger.info("loaded program configurations")
    # save this for later!
    # songs = read_from_bookmarks(configs["bookmarks"])
    songs = read_from_excel(configs["xlsx_file_name"])
    # print(songs)
    # csv_file_name = configs["csv_file_name"]
    # songs = read_from_csv(csv_file_name)
    # songs.to_excel(configs["xlsx_file_name"], index_label="Index")
    # song_list = dict(songs.values.tolist())
    # save this for later
    # write_to_csv(csv_file_name, songs)
    (songlist_item_name,
     songlist_item_url) = random.choice(songs.values.tolist())
    logger.info(f"opening {songlist_item_name} using {songlist_item_url}")
    chrome_path = r'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(songlist_item_url, 2)
