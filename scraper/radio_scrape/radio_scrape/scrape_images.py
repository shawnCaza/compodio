from posixpath import split
import random
import time
import etc_MySQL
import json, requests
import pathlib
import PIL
from PIL import Image
import os
import glob
import shutil

import util
import image_colour


def setup_save_folder(save_folder_base, slug):
    image_folder_path = pathlib.Path(save_folder_base + slug)
    image_folder_path.mkdir(parents=True, exist_ok=True)
    save_base = f"{save_folder_base}{slug}/{slug}"

    return save_base

def download_img(save_base, img, ext):
    """
        Downloads img from url as jpg, creates .webp version, and set of responsive image sizes.
        Returns array of {w: x, h: y} dicts for responsive image sizes, 
    """

    with open(f"{save_base}.{ext}", 'wb') as f:
        f.write(requests.get(img).content)

    image = Image.open(f"{save_base}.{ext}")
    image = image.convert('RGB')
    image.save(f"{save_base}.webp", 'webp', lossless=0, quality=50)            
    
    sizes_used = generate_sizes(image, save_base)


    return sizes_used

def generate_sizes(image, save_base, sizes=[250,350,500,750,1000,1250,1500,1750,2000,2400], formats=['webp','jpeg']):
    """
        Creates multiple sizes versions of an image.
        `image` = Pillow Image object
        'save_base` = Local folder path and base for the file name. Width and format extention will be added to this base when saving individual files.
        `sizes` = A list containing the file widths to be created.
        `formats` = The file types to be created for each image width. Values must be compatible with the Pillow Image format parameters.
    """
    sizes_used = []
    
    for format in formats:    
        for size in sizes:
            im = image.copy()
            
            if im.size[0] > size:
                
                im.thumbnail(size=((size, size)))

                if(format == 'jpeg'):
                    ext = 'jpg'
                    im.save(f"{save_base}_{str(size)}.{ext}", format, optimize=1)
                else:
                    ext = format
                    im.save(f"{save_base}_{str(size)}.{ext}", format, lossless=0, quality=50)
                
                sizes_used.append({'w': im.size[0], 'h': im.size[1] })
                    
    return sizes_used

def scrape_images():
                          
    save_folder_base ='/Users/scaza/Sites/compodio_images/shows/'

    mySQL = etc_MySQL.MySQL() 
    shows = mySQL.get_query("""
        SELECT id, slug, img, last_updt
        FROM shows
        LEFT JOIN show_images ON show_id = id
    """)

    folders_to_sync_list = [] # scraped images will be synched to remote server after being processed locally
    
    for show in shows:

        if len(show['img']) and show['slug']:

            src_last_updt = util.sever_file_last_update(show['img'])

            if show['last_updt']:
                needs_updt = True if show['last_updt'] < src_last_updt else False
            else:
                needs_updt = True

            if needs_updt:

                folders_to_sync_list.append(show['slug'])

                save_file_base = setup_save_folder(save_folder_base, show['slug'])

                sizes = download_img(save_file_base, show['img'], "jpg")

                dom_colours = image_colour.find_dominant_colours(f"{save_file_base}.jpg")
                
                print(show['id'], src_last_updt, sizes, json.dumps(dom_colours))
                
                mySQL.insert_image(show['id'], src_last_updt, json.dumps(sizes), json.dumps(dom_colours))
                time.sleep(15)
    
    
    # TODO synch new files to remote server

    
# TODO 
# def remove_unused_images():
#     # Should also delete records from image table and server if a certain age?
#     mySQL = etc_MySQL.MySQL()                           
#     save_folder_base =''

#     shows = mySQL.get_query("")

#     for show in shows:
#         folder_to_remove = save_folder_base + show['slug']
#         if folder_to_remove:
#             shutil.rmtree(folder_to_remove)
#             time.sleep(.25)


if __name__ == '__main__':
    scrape_images()
    