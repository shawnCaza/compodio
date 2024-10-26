import time
import json, requests
import pathlib
import math
from datetime import datetime
from typing import TypedDict

from PIL import Image, ImageOps

from util import sever_file_last_update
import image_colour
import scraper_MySQL
from server_sync.sync_compodio_data_to_server import synch_image_files

class Show(TypedDict):
    id: int
    slug: str
    img_url: str
    last_updt: datetime

def scrape_images():
                          
    save_folder_base ='/Users/scaza/Sites/compodio_images/shows'
    mySQL = scraper_MySQL.MySQL()
    shows = _all_shows(mySQL)
    folders_to_sync = [] # scraped images will be synched to remote server after being processed locally
    
    for show in shows:

        remote_modified_dt = sever_file_last_update(show['img_url'])

        if _show_has_image(show) and _needs_update(show, remote_modified_dt):

            _setup_save_folder(save_folder_base, show['slug'])

            saved_file_path = _download_img(save_folder_base, show)

            sizes = determine_sizes(orig_w=image.size[0], orig_h=image.size[1])
            sizes_created = generate_sizes(image, save_file_base, sizes)

            # Use the largest processed image for colour analysis. 
            # Original image might not be an expected format.
            img_path_for_colours = f"{save_file_base}_{sizes[-1]['w']}.jpg"
            try:
                dom_colours = image_colour.dominant_colours(img_path_for_colours)
            except Exception as e:
                print(f"Error calculating dominant image colours for show {show['id']}: {e}")
                dom_colours = None
                        
            if not remote_modified_dt:
                # Since server didn't return a last-modified header, 
                # we'll save the current date as a refernce point for future comparisons.
                remote_modified_dt = datetime.now()

            mySQL.insert_image(show['id'], remote_modified_dt, json.dumps(sizes_created), json.dumps(dom_colours))
            folders_to_sync.append(show['slug'])
            time.sleep(15) # To avoid overloading the server with requests
        else:
            time.sleep(1.5)
    
    # Send new images to remote server
    synch_image_files(save_folder_base, folders_to_sync)

def _all_shows(mySQL: scraper_MySQL.MySQL)->list[Show]:
     
    shows = mySQL.get_query("""
        SELECT id, slug, img as img_url, last_updt
        FROM shows
        LEFT JOIN show_images ON show_id = id
    """)
    return shows

def _show_has_image(show:Show)-> bool:
    return bool(show['img'] and len(show['img']) and show['slug'])

def _needs_update(show:Show, remote_modified_dt:datetime|None)-> bool:
    
    if show['last_updt'] and remote_modified_dt:
        # We can have both remote and local modified dates to compare
        needs_updt = True if show['last_updt'] < remote_modified_dt else False

    elif remote_modified_dt is None and show['last_updt']: 
        #To handle cases where the server doesn't return a last-modified header
        #todo: add a check to see if the file has changed by comparing file size
        needs_updt = False

    else:
        # Show image has never been downloaded
        needs_updt = True

    return needs_updt

def _setup_save_folder(save_folder_base:str, slug:str):
    image_folder_path = pathlib.Path(f"{save_folder_base}/{slug}")
    image_folder_path.mkdir(parents=True, exist_ok=True)

def _download_img(save_folder_base:str, show:Show):
    """
        Downloads img from url and saves it to the local folder in appropriate formats.
        Name of the file is based on the show slug. 
    """
    save_file_base = f"{save_folder_base}/{show['slug']}/{show['slug']}"
    ext = show['img_url'].split('.')[-1]
    temp_img_path = f"{save_file_base}_temp.{ext}"

    with open(temp_img_path, 'wb') as f:
        f.write(requests.get(show['img_url']).content)

    

def _open_image(img_path):
    image = Image.open(f"{save_file_base}.{ext}")
    image = ImageOps.exif_transpose(image) # Corrects orientation of image based on exif data
    image = image.convert('RGB')
    image.save(f"{save_file_base}.webp", 'webp', lossless=0, quality=50)

    return image

def determine_sizes(orig_w, orig_h):
    """
        Because images are often not the same aspect ratio as the responsive image container, 
        the image dimensions we need depend on the aspect ratio of the image compared to
        max-heights/widths allowed by css. As such, the values used here to calculate 
        the image sizes are coupled with the css max-widths, max-heights, and margins 
        values used across various screen sizes.
    """

    aspect_ratio = orig_w / orig_h

    sizes = [] # array of image

    # potential image margins and max width/height for each breakpoint used in css
    image_breakpoint_contraints = [
        {'w':None, 'h':180, 'margin':40}, 
        {'w':334, 'h':188, 'margin':24}, 
        {'w':386, 'h':218, 'margin':24}, 
        {'w':398, 'h':224, 'margin':24}, 
        {'w':None, 'h':280, 'margin':0}
    ]

    for constraints in image_breakpoint_contraints:

        # margin is applied to image area only when the eight is proportionally larger than a 16:9 aspect ratio
        margin = constraints['margin'] if aspect_ratio < 16/9 or constraints['margin'] == 40 else 0

        # The available with for the image is constrained by the max height and margin
        available_w = math.ceil((constraints['h']- margin) * aspect_ratio)

        new_w = available_w if not constraints['w'] or available_w < constraints['w'] else constraints['w']

        sizes.append(new_w)
        # add 2x and 3x sizes to account for retina displays
        sizes.append(new_w*2)
        sizes.append(new_w*3)

    sizes.sort()
    return sizes

def generate_sizes(image, save_base, sizes=[250,350,500,750,1000,1250,1500,1750,2000,2400], formats=['webp','jpeg']):
    """
        Creates multiple size versions of an image.
        `image` = Pillow Image object
        'save_base` = Local folder path and base for the file name. Width and format extention will be added to this base when saving individual files.
        `sizes` = A list containing the file widths to be created.
        `formats` = The file types to be created for each image width. Values must be compatible with the Pillow Image format parameters.
    """
    sizes_used = []
    
    for new_w in sizes:
        
        orig_w = image.size[0]
        orig_h = image.size[1]
        
        # We only want to create smaller images. No upscaling.
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