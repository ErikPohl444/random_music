import webbrowser
import pandas as pd
import random
import json


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
    print(bookmarks_names_urls)
    prepared_dict = {i: x for i, x in enumerate(bookmarks_names_urls.items())}

    bookmarks_names_urls = pd.DataFrame.from_dict(
        prepared_dict,
        orient="index",
        columns=['Song_Name', 'Song_URL']
    )
    print(bookmarks_names_urls)
    return bookmarks_names_urls


def write_to_csv(csv_file_name, song_list):
    song_list.to_csv(
        csv_file_name,
        columns=['Song_Name', 'Song_URL'],
        index_label="Index"
    )


def read_from_csv(csv_file_name):
    song_list = pd.read_csv(
        csv_file_name,
        header=0,
        names=['Song_Name', 'Song_URL']
    )
    return song_list


if __name__ == '__main__':
    with open("config.json") as config_handle:
        configs = json.load(config_handle)
    # save this for later!
    songs = read_from_bookmarks(configs["bookmarks"])
    print(songs)
    csv_file_name = configs["csv_file_name"]
    # songs = read_from_csv(csv_file_name)
    songs.to_excel("test.xlsx", index_label="Index")
    # song_list = dict(songs.values.tolist())
    # save this for later
    # write_to_csv(csv_file_name, songs)
    (songlist_item_name,
     songlist_item_url) = random.choice(songs.values.tolist())
    print(f"opening {songlist_item_name} using {songlist_item_url}")
    chrome_path = r'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(songlist_item_url, 2)
