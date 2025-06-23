# compodio

Work in progress, currently online at [https://www.compodio.com](https://www.compodio.com).

Some community radio stations post audio recordings of their shows online, but do not provide a podcast feed. This project provides RRS feeds for radio shows along side a UI with search and categorization features.

## Overview

### frontend folder

Contains a next.js project using react-query for server state, CSS modules for styling, and fuse.js for search.

### scraper folder

Contains a Python Scrapy project with [spiders](scraper/radio_scrape/radio_scrape/spiders) that scrapes show data from radio station websites.

In addition:

[scrape_images.py](scraper/radio_scrape/radio_scrape/image_colour.py) downloads show images and uses Pillow to generate a set of responsive images for the UI.

OpenAI Whisper is used to transcribe audio files, identify language, and Open source summarization models are used to create episode summaries in ai_ep_summary.py

Sci-kit learn is used to:

- Generate tags for shows based on their descriptions in show_keywords.py
- Perform k-means clustering on show image colours in [image_colour.py](scraper/radio_scrape/radio_scrape/image_colour.py) in order to generate the show-specific CSS gradients used in the UI.

### api folder

Contains a php api, and the podcast feed generator.

The api fetches data from a mysql database and returns it as json for the UI to consume.

`data/public/index.php` is the entry point for podcast feeds. It includes `data/private/feed_retreiver.php` to fetch data from the database and generates rss feeds for each show.

### db folder

Contains database schema and sample data

## Development

### Prerequisites

Using docker is recommended to simplify development setup.

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [docker-compose](https://docs.docker.com/compose/install/) (if not included with Docker Desktop)

<### Quick Start

1. Set up your .env file

   - Duplicate .env.example to .env
   - In most cases, the default values are all you need.

2. **Start all services:**

   ```bash
   docker-compose up -d --build
   ```

3. **Access the services:**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **API:** [http://localhost:8000](http://localhost:8000)
   - **Database:** MySQL is available on the port specified in your `.env` file (default 3307)

4. **Stopping services:**

   ```bash
   docker-compose down
   ```

### Notes

- All SQL files in the `db` folder will be executed on database startup. This seeds the database with sample data.
- For development, code changes in the `frontend`, `api`, and `scraper` folders will be reflected in the running containers due to volume mounts.
- If you encounter issues with environment variables, try restarting your terminal and running `docker-compose down` before `docker-compose up`.
