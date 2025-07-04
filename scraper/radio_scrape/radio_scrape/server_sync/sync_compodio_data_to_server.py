import os

from dotenv import load_dotenv


from radio_scrape.radio_scrape.server_sync.Sync_helper import Sync_helper
from radio_scrape.radio_scrape.scraper_MySQL import MySQL


def sync_db():
    server_syncer = Sync_helper()

    # Use db folder as save folder
    server_syncer.synch_tables(
        os.getenv("DB_EXPORT_PATH"),
        "02-complete_show_data.sql",
        "complete_show_data.tar.gz",
    )


def synch_image_files():
    load_dotenv()
    images_folder = f"{os.getenv('LOCAL_IMAGE_PATH')}/shows"

    mySQL = MySQL()
    shows = mySQL.show_images_to_sync()

    if len(shows) == 0:
        return

    folders_to_compress = [show["slug"] for show in shows]

    server_syncer = Sync_helper()
    compressed_image_files = "new_show_images.tar.gz"
    server_syncer.compress_folders(
        images_folder, folders_to_compress, compressed_image_files
    )

    ssh = server_syncer.connect()

    server_syncer.transfer(ssh, images_folder, compressed_image_files)

    server_syncer.remote_extract(
        ssh, compressed_image_files, "./images.compodio.com/shows"
    )

    mySQL.update_synced_show_images(folders_to_compress)


if __name__ == "__main__":

    synch_image_files()
    sync_db()
