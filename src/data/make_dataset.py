# -*- coding: utf-8 -*-
"""
make_dataset.py: Walks the raw data dirs and cleans the files placing them in the associated processed directory.
"""

__author__      = "Tyler Marrs"

import os
import sys

# Hack to get src dir on module path
project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

if project_dir not in sys.path:
   sys.path.append(project_dir)

from src import corpus
import re

tagged = re.compile('\[.*\]')
produced = re.compile('[p|P]roduced.*')

def clean_lyrics(lyrics):
    """Cleans the lyrics text."""
    new_lyrics = tagged.sub('', lyrics)
    new_lyrics = produced.sub('', new_lyrics)
    
    return new_lyrics


def main():
    processed_dir = corpus.processed_data_dir()
    
    for raw_dir in corpus.raw_data_dirs():
        
        #create new processed dir
        dir_name = raw_dir.split('/')[-1]
        new_dir = os.path.join(processed_dir, dir_name)
        os.makedirs(new_dir, exist_ok=True)
        
        for f_name in os.listdir(raw_dir):
            new_file = os.path.join(new_dir, f_name)
            
            # copy file content to new processed file cleaning lyrics as required
            with open(os.path.join(raw_dir, f_name)) as raw_file:
                file_content = raw_file.read()
                with open(new_file, 'wt') as processed_file:
                    if not f_name == 'songs.csv':                    
                        file_content = clean_lyrics(file_content)
                        
                    processed_file.write(file_content)
    
if __name__ == '__main__':
    main()