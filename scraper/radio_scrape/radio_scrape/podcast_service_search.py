from scraper_MySQL import MySQL

import requests
from xml.dom.minidom import parseString
import time
import os

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


mySQL = MySQL()




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
        feed_text = requests.get(potential_show_match["feedUrl"]).text
        try:
            feed = parseString(feed_text)
        except:
            print("Error parsing feed")
            feed = None
            continue

        # Lets look for clues that will help us determine if this is the correct podcast
        if show['source'].upper() in feed_text:
            print("- show source found in feedUrl")
            return exact_title_matches[0]["collectionViewUrl"], exact_title_matches[0]["feedUrl"]
        elif show['host'] and len(show['host'].split()) > 1 and show['host'] in potential_show_match['artistName']:
            print("- show host found in artistName")
            return exact_title_matches[0]["collectionViewUrl"], exact_title_matches[0]["feedUrl"]
        elif feed:
            raw_description_txt = feed.getElementsByTagName('description')[0].firstChild.nodeValue
            # reduce to one paragraph if description contains markup
            clean_description_txt = raw_description_txt.split('</p>')[0].replace('<p>','')
            if len(show['desc']) and show['desc'] in clean_description_txt: #seems like the values should be swithed around the 'in' operator
                print("- show description found in feedUrl")
                return exact_title_matches[0]["collectionViewUrl"], exact_title_matches[0]['feedUrl']

    # for result in results:
    #     if show_name.lower().replace(' ','') in result["collectionName"].lower().replace(' ',''):
    #         print("- potential match:", result["collectionName"])
    return None, None

def add_feed_link_2_db(show_id, link , feed_type):
    mySQL.insert_ext_feed_link({'show_id': show_id, 'link':link, 'feed_type':feed_type})

def verified_show_match(show, text_to_search, artist, description):
    # Lets look for clues that will help us determine if this is the correct podcast    

    # Define city associated with show, so we can search for it in the description later
    if(show['source'] == 'cfru'):
        city = 'guelph'
    elif(show['source'] == 'ciut'):
        city = 'toronto'
    else:
        city = None

    if show['source'].upper() in text_to_search:
        print("- show source reference found")
        return True
    
    elif show['host'] and len(show['host'].split()) > 1 and show['host'] in artist:
        print("- show host found in artistName")
        return True
    
    elif artist in show['desc']:
        print("- show artist found in podcast description")
        return True
    
    elif len(show['desc']) and show['desc'].split('</p>')[0].replace('<p>','') in description: 
            print("- show description found in podcast description")
            return True
    
    elif city and city in description.lower():
        print(f"- Station city '{city}' found in podcast description")
        return True
    


# get all shows without external links
shows = mySQL.get_shows_without_ext_feed_link_by_feedType('spotify')
for show in shows:

    # apple_link, rss_link = search_itunes_api(show)
    # if apple_link:
    #     print(apple_link, rss_link)
    #     add_feed_link_2_db(show['id'], apple_link, 'apple')

    # if rss_link:
    #     add_feed_link_2_db(show['id'], rss_link, 'rss')

    
    load_dotenv()
    spotify_client_id = os.getenv("spotify_client_id")
    spotify_client_secret = os.getenv("spotify_client_secret")

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id,client_secret=spotify_client_secret))

    results = sp.search(q=show['showName'], type='show', market='CA', limit=20)

    shows_with_exact_title_match = [result for result in results['shows']['items'] if show['showName'].lower()in result['name'].lower()]

    if len(shows_with_exact_title_match) == 1:
        
        print("\n\n***", show['showName'])
        for result in shows_with_exact_title_match:
            print("\n\n-")
            print(result['name'])
            print(result["external_urls"]['spotify'])
            print(result["images"][0]['url'])
            # print(result['description'])
            # print(f"*{result['publisher']}*")
            # print(result['languages'])
            # print(result['href'])
            # print(result['external_urls'])

            if verified_show_match(show, result['description'], result['publisher'].strip(), result['description']):
                print("verified show match")
                add_feed_link_2_db(show['id'], result["external_urls"]['spotify'], 'spotify')
                break
            
    time.sleep(2) # to avoid rate limiting
