# scrapes Townes van Zandt lyrics
# sample code so I don't have to remember all of this stuff
# the next time I want to source some verses

from bs4 import BeautifulSoup as soup
import requests
import string

punctuation_trans_table = str.maketrans("", "", string.punctuation)

def strip_punctuation(s): 
    return s.translate(punctuation_trans_table)

base_url = "http://ippc2.orst.edu/coopl/lyrics/"

index = requests.get(base_url + "albums.html")
parsed_index = soup(index.text)

all_links = parsed_index.find_all("a")    # get all <a> tags
links = [l for l in all_links if l.text]  # filter out image links, which have no text


def to_filename(s, path="texts/townes_van_zandt/"):
    '''Quick and dirty snake-casing'''
    s = s.replace("&amp;", "and")  # special case, "Poncho & Lefty"
    s = strip_punctuation(s)
    s = s.lower()
    s = s.replace(" ", "_")
    s = path + s + ".txt"
    return s



def process_link(link):
    title = link.text
    f = open(to_filename(title), "w")
    remote_file = link.get("href")
    song_file = requests.get(base_url + remote_file)
    verses = [l for l in soup(song_file.text).find_all("font") if l.get("size")]
    for verse in verses:
        if verse.text:
            f.writelines("\n".join(verse.stripped_strings))
            f.write("\n\n")
                                                                        

