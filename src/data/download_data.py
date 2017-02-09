# -*- coding: utf-8 -*-
"""
download_data.py: Downloads the latest and greats Billboard Hot 100 songs and lyrics placing 
them in new raw data folder with todays data.
"""

__author__      = "Tyler Marrs"

import os
import sys

# Hack to get src dir on module path
project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

if project_dir not in sys.path:
   sys.path.append(project_dir)

from src import webscrapers
from slugify import slugify
import time
import csv


def create_dirs():
    """
    Creates the directories for saving the raw data to.
    """
    raw_data_dir = os.path.join(project_dir, 'data', 'raw')
    save_dir = os.path.join(raw_data_dir, time.strftime("%d-%m-%Y"))
    
    os.makedirs(save_dir, exist_ok=True)
    
    return save_dir


def save_lyrics(save_dir, artist, title, lyrics):
    """
    Writes the lyrics file to the saved dir sluggifying the artist and title as the file name.
    """
    slugged = slugify(artist + ' ' + title, only_ascii=True) + '.txt'
    save_path = os.path.join(save_dir, slugged)
    
    try:
        f = open(save_path, 'w')
        f.write(lyrics)
    except:
        save_path = ''
    
    return save_path
    

def save_hot_100_and_lyrics():
    """
    Saves the songs and lyrics to data/raw/{dd-mm-yyyy} folder.
    """
    # create directories to save data to
    save_dir = create_dirs()
    
    # set up csv writer to write songs to
    hot_100_csv_path = os.path.join(save_dir, 'songs.csv')
    hot_100_csv = open(hot_100_csv_path, 'w')
    csv_writer = csv.writer(hot_100_csv, dialect='excel')
    csv_writer.writerow(['artist', 'title', 'rank_this_week', 'rank_last_week', 'lyrics_source', 'lyrics_file'])
    
    for song in webscrapers.get_billboard_hot_100():        
        source, lyrics = webscrapers.get_lyrics_search_all(song['artist'], song['title'])
        if lyrics is None:
            raise "Unable to fetch lyrics for: " + song['artist'] + " " + song['title']
            
        # save lyrics to file and write song to csv
        lyric_file_path = save_lyrics(save_dir, song['artist'], song['title'], lyrics)
        csv_writer.writerow([
            song['artist'],
            song['title'],
            song['rank_this_week'],
            song['rank_last_week'],
            source,
            lyric_file_path.split('/')[-1]
        ])
        
    hot_100_csv.close()


def save_swear_words():
    """
    Saves the swear words from noswearing.com to a text file in processed.
    """
    processed_data_dir = os.path.join(project_dir, 'data', 'processed')
    words = ['niggas']
    save_file = os.path.join(processed_data_dir, 'swear-words.txt')
    
    base_url = 'http://www.noswearing.com/dictionary/'
    letters = '1' + string.ascii_lowercase
    
    for letter in letters:
        full_url = base_url + letter
        result = requests_get(full_url)
        tree = html.fromstring(result.text)
        search = tree.xpath("//td[@valign='top']/a[@name and string-length(@name) != 0]")
        
        if search is None:
            continue
        
        for result in search:
            words.append(result.get('name').lower())
            
    with open(save_file, 'wt') as f:
        for word in words:
            f.write(word)
            f.write('\n')
    
    return words


def main():
    save_hot_100_and_lyrics()
    save_swear_words()
    
    
if __name__ == '__main__':
    main()