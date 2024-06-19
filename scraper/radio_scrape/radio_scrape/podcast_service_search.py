from scraper_MySQL import MySQL

import requests
from xml.dom.minidom import parseString
import time
import os

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


mySQL = MySQL()

def search_external_podcast_services():
    find_apple_feeds()
    find_spotify_feeds()

def find_apple_feeds():
    # get all shows without external links
    shows = mySQL.get_shows_without_ext_feed_link_by_feedType('apple')
    for show in shows:
        apple_link, rss_link = search_itunes_api(show)
        if apple_link:
            print(apple_link, rss_link)
            add_feed_link_2_db(show['id'], apple_link, 'apple')

        if rss_link:
            add_feed_link_2_db(show['id'], rss_link, 'rss')
        
        time.sleep(2) # to avoid rate limiting

def search_itunes_api(show):
    show_name = show['showName']
    parameters = {
        "term": show_name,
        "media": "podcast",
        "entity": "podcast",
        "attribute": "titleTerm"
    }
    
    response = requests.get("https://itunes.apple.com/search", params=parameters)
    
    results = response.json()["results"]

    exact_title_matches = [result for result in results if result["collectionName"].lower() == show_name.lower()]

    

    for potential_show_match in exact_title_matches:
        print("\n\n***", show['showName'])
        print("- exact match:", potential_show_match["collectionName"])
        # parse as xml to check if show['source'] is in feedUrl
        try:
            feed_request = requests.get(potential_show_match["feedUrl"], allow_redirects=True)
            feed_text = feed_request.text
            potential_show_match["feedUrl"] = feed_request.url
            try:
                feed = parseString(feed_text)
            except:
                print("Error parsing feed")
                feed = None
                continue
            if feed:
                raw_description_txt = feed.getElementsByTagName('description')[0].firstChild.nodeValue
                # reduce to one paragraph if description contains markup
                clean_description_txt = raw_description_txt.split('</p>')[0].replace('<p>','')

                if verified_show_match(show, feed_text, potential_show_match['artistName'], clean_description_txt):
                    print("verified show match")
                    return potential_show_match["collectionViewUrl"], potential_show_match['feedUrl']
        except:
            print("Error getting feed")
            continue

    time.sleep(2) # to avoid rate limiting
    # for result in results:
    #     if show_name.lower().replace(' ','') in result["collectionName"].lower().replace(' ',''):
    #         print("- potential match:", result["collectionName"])
    return None, None

def find_spotify_feeds():  
    
    shows = mySQL.get_shows_without_ext_feed_link_by_feedType('spotify')
    for show in shows:
        spotify_link = search_spotify_api(show)
        if spotify_link:
            add_feed_link_2_db(show['id'], spotify_link, 'spotify')
        
        time.sleep(2) # to avoid rate limiting

def search_spotify_api(show):
    load_dotenv()
    spotify_client_id = os.getenv("spotify_client_id")
    spotify_client_secret = os.getenv("spotify_client_secret")

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id,client_secret=spotify_client_secret))
    results = sp.search(q=show['showName'], type='show', market='CA', limit=20)

    shows_with_exact_title_match = [result for result in results['shows']['items'] if show['showName'].lower()in result['name'].lower()]

    if len(shows_with_exact_title_match) and show['id']:
        
        print("\n\n***", show['showName'])
        for result in shows_with_exact_title_match:
            print("\n\n-")
            print(result['name'])
            print(result["external_urls"]['spotify'])
            print(result["images"][0]['url'])
            print(result['description'])
            print(f"*{result['publisher']}*")
            # print(result['languages'])
            # print(result['href'])
            # print(result['external_urls'])

            if verified_show_match(show, result['description'], result['publisher'].strip(), result['description']):
                print("verified show match")
                return result["external_urls"]['spotify']

def verified_show_match(show, text_to_search, artist, description):
    # Lets look for clues that will help us determine if this is the correct podcast    

    # Define city associated with show, so we can search for it in the description later
    if(show['source'] == 'cfru'):
        city = 'guelph'
    elif(show['source'] == 'ciut'):
        city = 'toronto'
    elif(show['source'] == 'ckut'):
        city = 'montreal'
    else:
        city = None

    if show['source'].upper() in text_to_search:
        print("- show source reference found")
        return True
    
    elif show['host'] and len(show['host'].split()) > 1 and show['host'] in artist:
        print("- show host found in artistName")
        return True
    
    elif artist in show['desc'] and artist not in show['showName']:
        print("- show artist found in podcast description")
        return True
    
    elif len(show['desc']) and show['desc'].split('</p>')[0].replace('<p>','') in description: 
            print("- show description found in podcast description")
            return True
    
    elif city and city in description.lower():
        print(f"- Station city '{city}' found in podcast description")
        return True
    
def add_feed_link_2_db(show_id, link , feed_type):
    mySQL.insert_ext_feed_link({'show_id': show_id, 'link':link, 'feed_type':feed_type})


if __name__ == "__main__":
    search_external_podcast_services()