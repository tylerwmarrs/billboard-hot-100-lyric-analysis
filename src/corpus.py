# -*- coding: utf-8 -*-
"""corpus.py: Provides utility functions loading data from the billboard hot 100 list and lyrics."""

__author__      = "Tyler Marrs"

import os
import sys


def root_dir():
    """Helper to get the root path of this project."""
    return os.path.join(os.path.dirname(__file__), os.pardir)


def data_dir():
    """Helper to get the data dir path of this project."""
    return os.path.join(root_dir(), 'data')


def _data_path_for_dir(name):
    """Helper to get data path given a dir string name."""
    return os.path.join(data_dir(), name)


def _data_dirs(path):
    """Helper to get the list of directories in the given folder path."""
    data_dir = path
    dirs = [os.path.join(data_dir, d) for d in os.listdir(data_dir) 
            if os.path.isdir(os.path.join(data_dir, d))]
    
    return dirs


def raw_data_dir():
    """Helper to get the raw data dir path of this project."""
    return _data_path_for_dir('raw')


def raw_data_dirs():
    """Helper to get the list of directories in the raw data folder."""   
    return _data_dirs(raw_data_dir())


def processed_data_dir():
    """Helper to get the processed data dir path of this project."""
    return _data_path_for_dir('processed')


def processed_data_dirs():
    """Helper to get the list of directories in the processed data folder."""
    return _data_dirs(processed_data_dir())


def swear_words():
    """Helper to get the list of swear words from the processed data dir.
    
    Returns a list of strings.
    """
    fp = os.path.join(processed_data_dir(), 'swear-words.txt')
    words = []
    with open(fp, 'rt') as f:
        for line in f:
            words.append(line.strip())

    return words


def stop_words():
    """Helper to load custom list of stop words.
    
    Returns list of words.
    """
    fp = os.path.join(processed_data_dir(), 'stopwords.txt')
    words = []
    with open(fp, 'rt') as f:
        for line in f:
            words.append(line.strip())
            
    return words


def load_songs(dir_path):
    """Loads a list of songs and their lyrics from text files into a dictionary given folder path.
    
    Returns list of dictionaries.
    """
    song_file = os.path.join(dir_path, 'songs.csv')
    first_line = True
    keys = []
    songs = []
    with open(song_file) as f:
        for line in f:
            if first_line:
                first_line = False
                keys = line.strip().split(',')
                continue
                
            data = line.strip().split(',')
            index = 0
            song = {}
            for index, value in enumerate(data):
                key = keys[index]
                song[key] = value
                
                if key == 'lyrics_file':
                    lyrics_file_path = os.path.join(dir_path, value)
                    with open(lyrics_file_path) as lf:
                        song['lyrics'] = lf.read()
                        song['lyrics_file_path'] = lyrics_file_path
            
            songs.append(song)
        
    return songs