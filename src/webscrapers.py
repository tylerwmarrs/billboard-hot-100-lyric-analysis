"""webscrapers.py: Provides utility functions for web scraping the billboard hot 100 list and lyrics."""

__author__      = "Tyler Marrs"

from urllib.parse import urlencode
import re

import requests

from fake_useragent import UserAgent

from lxml import etree
from lxml import html
from lxml.etree import tostring


def _primary_artist(artist):
    """
    Utitlity function that tries to only get the main artist of a song.
    
    Example: "Tyler featuring Xyz" would just return "tyler"
    """
    artist = artist.casefold()
    artist = artist.split('featuring')[0].strip()
    artist = artist.split('/')[0].strip()
    artist = artist.split(' x ')[0].strip()

    return artist


def _requests_get(url, proxies={}):
    """
    Performs get request on the provided URL. It automatically adds a random user agent header and provides the option to add any proxy.
    """
    ua = UserAgent().random    
    return requests.get(url, headers={'User-Agent': ua}, proxies=proxies)


def get_billboard_hot_100():
    """
    Fetches the billboard hot 100 songs via RSS feed and returns a dictionary of the results.
    """
    hot_100_rss = _requests_get('http://www.billboard.com/rss/charts/hot-100')
    xml = bytes(bytearray(hot_100_rss.text, encoding='utf-8'))
    tree = etree.XML(xml)

    songs = []
    items = tree.xpath("//item")
    for item in items:
        song = {}

        song['title'] = item.xpath("chart_item_title/text()")[0]
        song['artist'] = item.xpath("artist/text()")[0]
        song['rank_this_week'] = item.xpath("rank_this_week/text()")[0]
        song['rank_last_week'] = item.xpath("rank_last_week/text()")[0]

        songs.append(song)
        
    return songs


def get_az_lyrics(artist, song_title):
    """
    Scrapes lyrics from the AZLyrics.com website.
    
    One caveat is that only the top search result is used in scraping the lyrics.
    """
    # search the AZLyrics site and scrape results
    artist = _primary_artist(artist)
    search_criteria = song_title + ' ' + artist
    
    base_url = 'http://search.azlyrics.com/search.php?'
    full_url = base_url + urlencode({'q': search_criteria})
    
    result = _requests_get(full_url)
    tree = html.fromstring(result.text)
    
    # Look for all URLs in search results
    # When no results - return None
    search_results = tree.xpath("//td/a[@target='_blank']")
    if not search_results:
        return None
    
    # Scrape the lyrics page for the lyrics
    lyrics_url = search_results[0].get('href')
    result = _requests_get(lyrics_url)
    tree = html.fromstring(result.text)
    
    lyrics_html = tree.xpath("//div")
    return lyrics_html[22].text_content()


def get_lyrics_freak(artist, song_title):
    """
    Fetches lyrics from LyricsFreak.com given artist and song_title. The best search result is found 
    by looking at all results and determining if a results matches both the artist and song.
    """
    artist = _primary_artist(artist)
    
    # search the LyricsFreak site and scrape results
    base_url = 'http://www.lyricsfreak.com'
    full_url = base_url + '/search.php?' + urlencode({'a': 'search', 'type': 'song', 'q': song_title})
    
    result = _requests_get(full_url)
    tree = html.fromstring(result.text)
    
    # Look for all URLs in search results
    # When no results - return None
    search_results = tree.xpath("//td/a")
    if not search_results:
        return None
    
    # find the lyrics page...
    previous_is_artist = False
    lyrics_url = None
    for result in search_results:
        current_text = result.text_content().casefold()
        if previous_is_artist and song_title.casefold() in current_text:
            lyrics_url = base_url + result.get("href")
            break        
        
        previous_is_artist = artist.casefold() in current_text
    
    if not lyrics_url:
        return None
    
    # scrape the lyrics
    result = _requests_get(lyrics_url)
    tree = html.fromstring(result.text)
    
    lyric_html = tree.xpath("//div[@id='content_h']")
    if not lyric_html:
        return None
    
    lyric_html = str(tostring(lyric_html[0]))
    return html.fromstring(re.sub(r'<br\w*\/?>', r'\\n', lyric_html)).text_content()


def get_song_lyrics(artist, song_title): 
    """
    Scrapes song lyrics from SongLyrics.com given artist and song title.
    """
    # search the SongLyrics site and scrape results
    base_url = 'http://www.songlyrics.com'
    params = {
        'section': 'search',
        'searchW': artist + ' ' + song_title,
        'submit': 'Search',
        'searchIn1': 'artist',
        'searchIn3': 'song'
    }
    full_url = base_url + '/index.php?' + urlencode(params)
    
    result = _requests_get(full_url)
    tree = html.fromstring(result.text)
    
    # Look for all URLs in search results
    # When no results - return None
    search_results = tree.xpath("//div[@class='serpresult']/h3/a")
    if not search_results:
        return None
    
    lyrics_url = search_results[0].get('href')
    
    if not lyrics_url:
        return None
    
    # scrape the lyrics
    result = _requests_get(lyrics_url)
    tree = html.fromstring(result.text)
    
    lyric_html = tree.xpath("//p[@id='songLyricsDiv']")
    if not lyric_html:
        return None
    
    return lyric_html[0].text_content()


def get_lyrics_search_all(artist, song_title):
    """
    Searches all song sites in attempt to find the song lyrics. It returns the lyrics and the source.
    
    Returns (source, lyrics) tuple
    """
    sources = {
        'songlyrics.com': get_song_lyrics,
        'lyricsfreak.com': get_lyrics_freak,
        'azlyrics.com': get_az_lyrics
    }
    
    lyrics = None
    source = None

    for s, func in sources.items():
        try:
            lyrics = func(artist, song_title)
        except Exception:
            pass

        if lyrics is not None:
            source = s
            break
    
    return (source, lyrics)
    
    