import time
import json, requests
import pathlib
import math

from PIL import Image

import util
import image_colour
import scraper_MySQL


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
    sizes = determine_sizes(orig_w=image.size[0], orig_h=image.size[1])
    sizes_used = generate_sizes(image, save_base, sizes)


    return sizes_used

def determine_sizes(orig_w, orig_h):
    """
        Because images are often not the same aspect ratio as the responsive image container, 
        the image widths we need depend on the aspect ratio of the image compared to max-heights/widths allowed in css/components.
    """

    aspect_ratio = orig_w / orig_h

    sizes = []

    for max in [{'w':None, 'h':180, 'margin':40}, {'w':334, 'h':188, 'margin':24}, {'w':386, 'h':218, 'margin':24}, {'w':398, 'h':224, 'margin':24}, {'w':None, 'h':280, 'margin':0}]:

        margin_height_reduction = max['margin'] if aspect_ratio < 16/9 or max['margin'] == 40 else 0

        new_potential_w = math.ceil((max['h']-margin_height_reduction) * aspect_ratio)

        new_w = new_potential_w if not max['w'] or new_potential_w < max['w'] else max['w']
        sizes.append(new_w)
        sizes.append(new_w*2)
        sizes.append(new_w*3)
    sizes.sort()
    return sizes

def generate_sizes(image, save_base, sizes=[250,350,500,750,1000,1250,1500,1750,2000,2400], formats=['webp','jpeg']):
    """
        Creates multiple sizes versions of an image.
        `image` = Pillow Image object
        'save_base` = Local folder path and base for the file name. Width and format extention will be added to this base when saving individual files.
        `sizes` = A list containing the file widths to be created.
        `formats` = The file types to be created for each image width. Values must be compatible with the Pillow Image format parameters.
    """
    sizes_used = []
    
        
    for new_w in sizes:
        
        orig_w = image.size[0]
        orig_h = image.size[1]

        if orig_w > new_w:
            
            decreace_percent = new_w / orig_w
            new_h = int(orig_h * decreace_percent)

            resized_image = image.resize(size=((new_w, new_h)))

            for format in formats:
                
                if(format == 'jpeg'):
                    ext = 'jpg'
                    resized_image.save(f"{save_base}_{str(new_w)}.{ext}", format, optimize=1)
                else:
                    ext = format
                    resized_image.save(f"{save_base}_{str(new_w)}.{ext}", format, lossless=0, quality=50)
            
            sizes_used.append({'w': resized_image.size[0], 'h': resized_image.size[1] })
                    
    return sizes_used

def scrape_images():
                          
    save_folder_base ='/Users/scaza/Sites/compodio_images/shows/'

    mySQL = scraper_MySQL.MySQL() 
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

                dom_colours = image_colour.find_avg_dominant_colours(f"{save_file_base}.jpg")
                
                print(show['id'], src_last_updt, sizes, json.dumps(dom_colours))
                
                mySQL.insert_image(show['id'], src_last_updt, json.dumps(sizes), json.dumps(dom_colours))
                time.sleep(15)
            else:
                time.sleep(1.5)
    
    
    # TODO synch new files to remote server

    
# TODO 
# def remove_unused_images():
#     # Should also delete records from image table and server if a certain age?
#     mySQL = scaper_MySQL.MySQL()                           
#     save_folder_base =''

#     shows = mySQL.get_query("")

#     for show in shows:
#         folder_to_remove = save_folder_base + show['slug']
#         if folder_to_remove:
#             shutil.rmtree(folder_to_remove)
#             time.sleep(.25)


if __name__ == '__main__':
    scrape_images()
    # print(determine_sizes(924,598))
    # print(determine_sizes(324,180))