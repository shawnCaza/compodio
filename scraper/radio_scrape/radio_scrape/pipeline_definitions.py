
def episode_pipelines():
    return {
    'radio_scrape.radio_scrape.pipelines.EncodeURL': 100,
    'radio_scrape.radio_scrape.pipelines.GetFileSize': 200,
    'radio_scrape.radio_scrape.pipelines.SaveEpisode': 300,
    }

def show_pipelines():
    return {
    'radio_scrape.radio_scrape.pipelines.ShowSlug': 100,
    'radio_scrape.radio_scrape.pipelines.SaveShow': 200,
    }

def external_feed_pipelines():
    return {
    'radio_scrape.radio_scrape.pipelines.SaveExtFeedLink': 100,
    }


