# compodio

Work in progress, currently online at [https://www.compodio.com](https://www.compodio.com).

Some community radio stations post audio recordings of their shows online, but do not provide a podcast feed. This project provides rrs feeds for radio shows along side a UI  with search and categoization features.

## Overview

### UI folder

Contains a [next.js](https://nextjs.org/) project using [react-query](https://react-query.tanstack.com/) for server state, CSS modules for styling, and [fuse.js](https://fusejs.io/) for search.

### scraper folder

Contains a python [Scrapy](https://scrapy.org/) project that scrapes show data from radio station websites.

In addition:

OpenAI Whisper is used to transcribe audio files, identify language, and Open source summarization models are used to create episode summaries in [ai_ep_summary.py](scraper/radio_scrape/radio_scrape/ai_ep_summary.py)

[Sci-kit learn](https://scikit-learn.org/stable/) is used to:
<!-- add bullets -->
- Generate tags for shows based on their descriptions in `show_keywords.py`
- Perform k-means clustering on show image colours in `image_colour.py` in order to generate the show specific CSS gradients used in the UI.

`scrape_images.py` downloads show images and uses [Pillow](https://pillow.readthedocs.io/en/stable/) to generate a set of responsive images for the UI.

### data folder
Contains a php api, and the podcast feed generator.

The api fetches data from a mysql database and returns it as json for the UI to consume.

`data/public/index.php` is the entry point for poddcast feeds. It includes `data/private/feed_retreiver.php` to fetch data from the database and generates rss feeds for each show.

### db folder
Contains database dumps

## Development

### Prerequisites

- [python 3.11](https://www.python.org/downloads/) 
- [next.js ^14.2.4](https://nextjs.org/docs/getting-started)
- [mysql 8.0.23](https://dev.mysql.com/downloads/mysql/)
- [php 8.2.3](https://www.php.net/downloads.php)

### Setup

1. **Clone the repo** to local server folder (required for the php portion of the project)
2. **Insall dependencies** for the portion(s) of the project you want to work with.

    It's possible to work on each aspect of the project independently.
    - For the NextJS UI [see the readme in the ui folder](ui/README.md)
    - For the Python scrapy project and scraper related scripts [see the README in the scraper folder](scraper/README.md)
    - For the PHP api and podcast feed generator [see the README in the data folder].

2. Install python dependencies: `pip install -r scraper/requirements.txt`
3. Install next.js dependencies in the UI folder: `npm install`
4. import database from `db/compodio.sql`
5. add db credentials for php to `data/private/db_credentials.php` using `data/private/db_credentials_default.php` as a template
6. add db credentials for python to `scraper/radio_scrape/radio_scrape/DBConfig.py` using `DBConfig-default.py` as a template
7. define local path for show images in `scraper/radio_scrape/radio_scrape/scrape_images.py`
8. In /UI add `.env.local` file with the following contents:
```
NEXT_PUBLIC_API_URI = 'http://localhost/path-to-project-folder/data/'
NEXT_PUBLIC_feed_URI = 'http://localhost/path-to-project-folder/feed/'
NEXT_PUBLIC_image_server_URI = 'http://localhost/compodio_images/'
```
