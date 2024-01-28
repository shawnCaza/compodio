from radio_scrape.radio_scrape.server_sync.Sync_helper import Sync_helper

def sync_db():

    server_syncer = Sync_helper()

    # Use db folder as save folder
    server_syncer.synch_tables('/Users/scaza/Sites/community-podcast/db', 'compodio.sql', 'compodio.tar.gz')


def synch_image_files(save_folder_base, folders_to_compress):
    
    server_syncer = Sync_helper()
    compressed_image_files = 'new_show_images.tar.gz'

    server_syncer.compress_folders(save_folder_base, folders_to_compress, compressed_image_files)

    ssh = server_syncer.connect()

    server_syncer.transfer(ssh, save_folder_base, compressed_image_files)

    server_syncer.remote_extract(ssh,compressed_image_files, './images.compodio.com/shows')


if __name__ == '__main__':
    # sync_db()
    save_folder_base ='/Users/scaza/Sites/compodio_images/shows'
    folders_to_sync = ["cfru-storied-lives"]
    synch_image_files(save_folder_base, folders_to_sync)