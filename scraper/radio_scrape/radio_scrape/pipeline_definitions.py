
def episode_pipelines():
    return {
    'radio_scrape.pipelines.GetFileSize': 100,
    'radio_scrape.pipelines.SaveEpisode': 200,
    }

def show_pipelines():
    return {
    'radio_scrape.pipelines.ShowSlug': 100,
    'radio_scrape.pipelines.SaveShow': 200,
    }


