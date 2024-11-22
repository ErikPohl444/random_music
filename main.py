import webbrowser
import pandas as pd
import random


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

def read_from_csv(csv_file_name):
    pass


if __name__ == '__main__':
    playlist = {}
    playlist = read_from_bookmarks('bookmarks_11_13_23.html')
    print(playlist)
    write_to_csv(playlist)
    name, url = random.choice(list(playlist.items()))
    print(f"opening {name} using {url}")
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(url, 2)
