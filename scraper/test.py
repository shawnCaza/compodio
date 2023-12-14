import requests

# make request to https://itunes.apple.com/search?term=breezy+breakfast&entity=podcast

parameters = {
    "term": "The Radical Reverend",
    "media": "podcast",
    "entity": "podcast",
    "attribute": "titleTerm"
}

response = requests.get("https://itunes.apple.com/search", params=parameters)

results = response.json()["results"]
for result in results:
    print("\n\n***")
    print(result["collectionName"])
    print(result["kind"])
    print(result["feedUrl"])
    print(result['artistName'])
    print(result['collectionViewUrl'])
    print(result['wrapperType'])


