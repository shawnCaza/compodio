import time
import json, requests
import pathlib
import math
from datetime import datetime
from typing import TypedDict, Literal
from dataclasses import dataclass, field

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

class ImageDimensions(TypedDict):
    w: int
    h: int

@dataclass
class ImageProps():
    folder: str
    remote_url: str
    remote_modified_dt: datetime | None = None
    base_name: str | None = None
    image: Image.Image | None = None
    responsive_widths: set[int] = field(default_factory=set)
    responsive_dimensions: set[ImageDimensions] = field(default_factory=set)

    @property
    def orig_ext(self) -> str:
        if self.remote_url and '.' in self.remote_url:
            return self.remote_url.split('.')[-1]
        else:
            raise ValueError("remote_url hasn't been properly defined")

    @property
    def temp_file_path(self) -> str | None:
        if self.folder and self.base_name and self.orig_ext:
            return f"{self.folder}/{self.base_name}_temp.{self.orig_ext}"
        else:
            raise ValueError("Not all path components have been defined.")
        
    @property
    def modified_for_db_dt(self) -> datetime:
        # If server didn't return a last-modified header, 
        # we'll use current date as a refernce point for future comparisons.
        return self.remote_modified_dt if self.remote_modified_dt else datetime.now()
    
def scrape_images():
                          
    save_folder_base ='/Users/scaza/Sites/compodio_images/shows'
    mySQL = scraper_MySQL.MySQL()
    shows = _all_shows(mySQL)
    folders_to_sync = [] # scraped images will be synched to remote server after being processed locally
    
    for show in shows:

        image_props = ImageProps(
            folder = f"{save_folder_base}/show['slug']",
            remote_url = show['img_url']
        )

        image_props.remote_modified_dt = sever_file_last_update(image_props.remote_url)

        if _show_has_image(show) and _needs_update(show, image_props):

            _setup_save_folder(image_props)

            _download_img(image_props)
            
            _open_image(image_props)

            _create_standard_image_versions(image_props)

            _determine_responsive_sizes(image_props)
            
            _generate_responsive_sizes(image_props)

            try:
                dom_colours = image_colour.dominant_colours(file_path(image_props,'jpg'))
            except Exception as e:
                print(f"Error calculating dominant image colours for show {show['id']}: {e}")
                dom_colours = None
                        
            mySQL.insert_image(
                show['id'], 
                image_props.modified_for_db_dt, 
                json.dumps(image_props.responsive_dimensions), 
                json.dumps(dom_colours)
            )
            folders_to_sync.append(show['slug'])
            time.sleep(90) # To avoid overloading the server with requests
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

def _needs_update(show:Show, image_props:ImageProps)-> bool:
    
    remote_modified_dt = image_props.remote_modified_dt

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

def _setup_save_folder(image_props:ImageProps):
    image_folder_path = pathlib.Path(image_props.folder)
    image_folder_path.mkdir(parents=True, exist_ok=True)

def _download_img(image_props:ImageProps) -> None:
    """
        Downloads img from url and saves it to 
        a temp local folder. 
    """

    with open(image_props.temp_file_path, 'wb') as f:
        f.write(requests.get(image_props.remote_url).content)

def _open_image(image_props:ImageProps) -> None:

    image_props.image = Image.open(image_props.temp_file_path)

def _create_standard_image_versions(image_props:ImageProps):

    if image_props.image is None:
        raise ValueError("Image not already open.")
    
    # Correct orientation of image based on exif data
    image_props.image = ImageOps.exif_transpose(image_props.image)
    image_props.image = image_props.image.convert('RGB')

    image_props.image.save(
        file_path(image_props, 'webp'),
        'webp', 
        lossless=0, 
        quality=50
    )

    image_props.image.save(
        file_path(image_props, 'jpg'),
        'jpeg',
        optimize=True
    )

def _determine_responsive_sizes(image_props:ImageProps):
    """
        Because images are often not the same aspect ratio as the responsive image container, 
        the image dimensions we need depend on the aspect ratio of the image compared to
        max-heights/widths allowed by css. As such, the values used here to calculate 
        the image sizes are coupled with the css max-widths, max-heights, and margins 
        values used across various screen sizes.
    """

    if image_props.image is None:
        raise ValueError("Image not already open.")
    
    orig_w = image_props.image.width
    orig_h = image_props.image.height

    aspect_ratio = orig_w / orig_h

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

        # Add new_w, along with retina sized variations, to responsive_widths
        # as long as we're not upscaling.
        widths_to_add = [new_w, new_w*2, new_w*3]

        for width in widths_to_add:
            if width < orig_w:
                image_props.responsive_widths.add(width)

def _generate_responsive_sizes(image_props: ImageProps):
    """
        Creates multiple size versions of an image.
        `image` = Pillow Image object
        'save_base` = Local folder path and base for the file name. Width and format extention will be added to this base when saving individual files.
        `sizes` = A list containing the file widths to be created.
        `formats` = The file types to be created for each image width. Values must be compatible with the Pillow Image format parameters.
    """
    if image_props.image is None:
        raise ValueError("Image has not been opened")

    for new_w in sorted(image_props.responsive_widths, reverse=True):
        
        current_w = image_props.image.size[0]
        current_h = image_props.image.size[1]
        
            
        decreace_percent = new_w / current_w
        new_h = int(current_h * decreace_percent)

        resized_image = image_props.image.resize(size=((new_w, new_h)))

        resized_image.save(
            file_path(image_props, 'jpg', str(new_w)),
            "jpeg",
            optimize=True
        )

        resized_image.save(
            file_path(image_props, 'webp', str(new_w)),
            "webp",
            lossless=0,
            quality=50
        )
        
        image_props.responsive_dimensions.add({'w': resized_image.size[0], 'h': resized_image.size[1] })
                    
def file_path(image_props:ImageProps, ext: str, id: str | None = None) -> str:

    if id is not None:
        return f"{image_props.folder}/{image_props.base_name}_{id}.{ext}"
    else:
        return f"{image_props.folder}/{image_props.base_name}.{ext}"
    

if __name__ == '__main__':
    scrape_images()
    # print(determine_sizes(924,598))
    # print(determine_sizes(324,180))