import os

from dotenv import load_dotenv

from radio_scrape.radio_scrape.server_sync.Sync_helper import Sync_helper
from radio_scrape.radio_scrape.scraper_MySQL import MySQL


def sync_sample_db():

    load_dotenv("scraper/radio_scrape/radio_scrape/.env")

    user_name = os.getenv("local_username")
    password = os.getenv("local_password")
    host = os.getenv("local_host")
    database = os.getenv("local_database")

    show_ids = sample_show_ids()

    # Format the list of IDs for SQL WHERE IN clause
    show_ids_str = ",".join(map(str, show_ids))

    # Build dump command with where conditions
    dump_file = "/app/sample-data/db-sample.sql"
    os.makedirs(os.path.dirname(dump_file), exist_ok=True)

    # Create list of tables that need filtering by show_id
    show_related_tables = [
        ("shows", "id"),
        ("episodes", "show_id"),
        ("show_tags", "show_id"),
        ("show_images", "show_id"),
        ("ext_feed_links", "show_id"),
    ]

    os.system(
        f"mysqldump -u{user_name} -p{password} -h{host} --no-data {database} > {dump_file}"
    )

    # Then dump data filtered by shows
    for table, id_field in show_related_tables:
        os.system(
            f'mysqldump -u{user_name} -p{password} -h{host} compodio {table} --where="{id_field} IN ({show_ids_str})" >> {dump_file}'
        )

    # Dump other tables that need to be included but aren't directly related to shows
    # For example all_tags table (or a filtered subset)
    os.system(
        f"mysqldump -u{user_name} -p{password} -h{host} compodio all_tags >> {dump_file}"
    )

    print(f"Sample database exported to {dump_file}")


def synch_sample_images():
    load_dotenv("scraper/radio_scrape/radio_scrape/.env")
    images_folder = f"{os.getenv('image_folder')}/shows"

    mySQL = MySQL()
    shows = mySQL.get_show_images()

    sample_shows = [show for show in shows if show["id"] in sample_show_ids()]

    folders_to_compress = [show["slug"] for show in sample_shows]

    server_syncer = Sync_helper()
    compressed_image_files = "sample_show_images.tar.gz"
    server_syncer.compress_folders(
        images_folder, folders_to_compress, compressed_image_files
    )

    ssh = server_syncer.connect()

    server_syncer.transfer(
        ssh, images_folder, compressed_image_files, f"./images.compodio.com"
    )


def sample_show_ids() -> list[int]:
    return [
        164,
        99,
        146,
        200,
        83,
        112,
        175,
        206,
        94,
        166,
        79,
        118,
        132,
        150,
        270053,
        270105,
        270056,
        102180,
        270042,
        270114,
        269984,
        270097,
        270100,
        269938,
        159,
        90,
        193,
        1344,
        3033,
        270094,
        126,
    ]


if __name__ == "__main__":
    sync_sample_db()
