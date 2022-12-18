import requests
headers = requests.head('https://ciut.fm/wp-content/uploads/audio/whatiship.mp3', stream=True).headers
print(headers)