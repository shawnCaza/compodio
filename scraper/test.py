
link = "https://www.podbean.com/player-v2/?i=3qis5-f742ce-pbblog-playlist&share=1&download=1&rtl=0&fonts=Arial&skin=1&font-color=auto&logo_link=episode_page&order=episodic&limit=10&filter=all&ss=a713390a017602015775e868a2cf26b0&btn-skin=1b1b1b&size=315"

#  Parse value for i in link query string
from urllib.parse import urlparse, parse_qs
parsed_url = urlparse(link)
qs = parse_qs(parsed_url.query)
print(qs)
