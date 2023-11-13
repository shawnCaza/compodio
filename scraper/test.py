import requests


header = requests.head("https://mcdn.podbean.com/mf/web/rs845a/November_10_2023_The_Cool_Side_of_The_Pillow6ptvs.mp3", stream=True)


print(header.status_code)
print(header.headers)

mp3 = "https://mcdn.podbean.com/mf/web/rs845a/November_10_2023_The_Cool_Side_of_The_Pillow6ptvs.mp3"

r = requests.head(mp3, stream=True)

if r.status_code == 200:

    print(r.status_code)
    print(r.headers)