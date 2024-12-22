import webbrowser
import pandas as pd
import random
import json

# output dictionary as spreadsheet
# class entries in spreadsheet by category
# select only entries in a category
# angular front end?


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
    return bookmarks_names_urls


def write_to_csv(song_list):
    (pd.DataFrame.from_dict(data=song_list, orient='index')
     .to_csv('dict_file.csv', header=False))


def read_from_csv():
    song_list = pd.read_csv('dict_file.csv', header=None)
    return song_list


if __name__ == '__main__':
    with open("config.json") as config_handle:
        configs = json.load(config_handle)
    # save this for later!
    # playlist = read_from_bookmarks(configs["bookmarks"])
    csv_file_name = configs["csv_file_name"]
    songs = read_from_csv(csv_file_name)
    song_list = dict(songs.values.tolist())
    # save this for later
    # write_to_csv(csv_file_name, song_list)
    (songlist_item_name,
     songlist_item_url) = random.choice(list(song_list.items()))
    print(f"opening {songlist_item_name} using {songlist_item_url}")
    chrome_path = r'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(songlist_item_url, 2)
