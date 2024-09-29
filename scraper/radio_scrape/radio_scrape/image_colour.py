from decimal import *
from dataclasses import dataclass
from dataclasses import field

import cv2
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import KMeans
from colormath.color_objects import  LabColor, sRGBColor, HSLColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# finding avg dominant colours in image
# from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv

# finding border colour from https://stackoverflow.com/questions/10985550/detect-if-an-image-has-a-border-programmatically-return-boolean

@dataclass(kw_only=True)
class CentralClusterColour:
    frequency: float # percentage of pixels in the cluster
    orig_rgb: sRGBColor # the original central colour of the cluster
    proccessed_rgb: sRGBColor = field(init=False) # the original colour after processing (So it competes less with the actual image).
    processed_lab: LabColor = field(init=False) 
    processed_hex: str = field(init=False)
    delta_E_from_white: float = field(init=False) 

    def __post_init__(self):
        self.processed_rgb = self.decontrast(self.desaturate(self.orig_rgb))
        self.processed_hex = self.processed_rgb.get_rgb_hex()
        self.processed_lab = convert_color(self.processed_rgb, LabColor, target_illuminant="d65")
        self.delta_E_from_white = delta_e_cie2000(self.processed_lab, LabColor(100, 0, 0,illuminant="d65"))


    def desaturate(self, rgb:sRGBColor) -> sRGBColor:
        """
            Desaturates a colour by converting it to hls and then back to sRGBColor.
        """
        # convert sRGB to hsl 
        hsl = convert_color(rgb, HSLColor)
        
        # desaturate a little more the more saturated it is
        hsl.hsl_s = hsl.hsl_s - ((hsl.hsl_s * 0.25) + (hsl.hsl_s / 65) * 5)

        # convert back to rgb
        return convert_color(hsl, sRGBColor)

    def decontrast(self, rgb:sRGBColor) -> sRGBColor:
        """
            Reduces contrast of a sRGBColor colour by converting it to Lab.
            Then clamping the lower and upper bounds of the L* value.
        """
        lab = convert_color(rgb, LabColor)
        if lab.lab_l > 60:
            # Too bright, reduce brightness. The brighter the more we reduce
            lab.lab_l = 60 + ((lab.lab_l - 60) * 0.4 )
        elif lab.lab_l < 20:
            # Too dark, increase brightness. The darker the more we increase

            # Make sure L is not less than 1 or crazy things happen in the next step
            lab.lab_l = lab.lab_l if lab.lab_l > 1 else 1
            # Make L at least ten, plus a bit more based on how dark it is
            lab.lab_l = 10 + (lab.lab_l * 0.5 ) + 20 / lab.lab_l * .15

        return convert_color(lab, sRGBColor)


def find_dominant_img_colours(image_path: str, quantity: int = 3) -> list[str]:
    """
        param image_path: string path to image file
        param quantity: int number of colours to return
        Returns: list with specified number of hex colours sorted from darkest to lightest. 
        If the image does not contain enough colouts, the list will be shorter.

        k-means clustering is used to cluster n similar colours together, and obtain the mean colour of each group.
        n is specified by the quantity parameter.

        These colours may then be processed in various ways to obtain results that are more suitable for use as a background gradient behing the image.

        Then sorted from darkest to lightest and returned as a list of hex colours.
    """
    # Load image and convert to a list of pixels
    image_data_RGB_2d = rgb_2d_pixel_array_from_image(image_path)

    # init kmeans - cluster the image data into the specified number of clusters
    clusters = KMeans(n_clusters=quantity).fit(image_data_RGB_2d)

    central_cluster_colours_and_frequencies_zip = group_cluster_colour_and_frequency(clusters)

    central_cluster_colours = []
    for (frequency, color) in central_cluster_colours_and_frequencies_zip:
         central_cluster_colours.append(CentralClusterColour(frequency=frequency, orig_rgb = sRGBColor(*color, is_upscaled=True)))

    colours_filtered_for_uniqueness = filter_for_uniqueness(central_cluster_colours)
 
    # Sort from darkest to lightest based on lab L* value
    colours_filtered_for_uniqueness.sort(reverse=False, key=lambda colour: colour.processed_lab.lab_l)
    
    filtered_lab_sorted_hex_colours = [colour.processed_hex for colour in colours_filtered_for_uniqueness]

    return filtered_lab_sorted_hex_colours

def rgb_2d_pixel_array_from_image(image_path: str) -> NDArray[np.uint8]:
    
    # Load image and convert to numpy array of pixels data
    image_data_BGR_3d = cv2.imread(image_path)
    image_data_RGB_3d = cv2.cvtColor(image_data_BGR_3d, cv2.COLOR_BGR2RGB)
    # Reshape to a list of pixels - Flatten the 3D array (pixel rows, pixel columns, RGB pixel data) to 2D (pixels, RGB pixel data)
    image_data_RGB_2d = image_data_RGB_3d.reshape((image_data_RGB_3d.shape[0] * image_data_RGB_3d.shape[1], 3))
    return image_data_RGB_2d

def group_cluster_colour_and_frequency(clusters: KMeans) -> list[tuple[float, NDArray[np.uint8]]]:
    """Returns list of named tuples containing (frequency, colorMath sRGBColor))"""

    # Generate a range of integers from 0 to the number of unique cluster labels (inclusive). 
    labels = np.arange(0, len(np.unique(clusters.labels_)) + 1)
    #histogram will give us the number of pixels for each cluster
    (cluster_pixel_counts, _) = np.histogram(clusters.labels_, bins = labels)
     
    # Normalize the histogram - divide by the total number of pixels to get the percentage of pixels in each cluster
    cluster_pixel_counts_float = cluster_pixel_counts.astype("float")
    cluster_frequencies = cluster_pixel_counts_float / cluster_pixel_counts_float.sum()

    # Group frequency of each cluster group, to the central colour of that cluster and then add it to the colours list
    
    return zip(cluster_frequencies, clusters.cluster_centers_)

def filter_for_uniqueness(colours: list[CentralClusterColour], min_delta:int=14) -> list[CentralClusterColour]:
    """
        Filters out colours that are too similar to each other.
        Prefering the colour withe a higher frequency level.
        Colours are considered too similar if the delta E is less than min_delta.

        returns list of filtered CentralClusterColour sorted in descending order by frequency.
    """
    colours.sort(reverse=True, key=lambda colour: colour.frequency)
    colours_filtered_for_uniqueness = [colours[0]]
    for pending_colour in colours[1:]:
        for existing_colour in colours_filtered_for_uniqueness:
            if delta_e_cie2000(pending_colour.processed_lab, existing_colour.processed_lab) < min_delta:
                break
        else:
            colours_filtered_for_uniqueness.append(pending_colour)

    return colours_filtered_for_uniqueness


# colormath is terribly out of date. 
# It uses numpy.asscalar for the delta_E calculation which is deprecated in numpy 1.20.0
# This is a hack to patch it. *sigh* (https://stackoverflow.com/a/76904868/1586014)
def patch_asscalar(a):
    return a.item()

setattr(np, "asscalar", patch_asscalar)


if __name__ == '__main__':


    import scraper_MySQL
    import json

    save_folder_base ='/Users/scaza/Sites/compodio_images/shows/'

    mySQL = scraper_MySQL.MySQL() 
    shows = mySQL.get_query("""
        SELECT id, slug, img, last_updt, sizes
        FROM shows
        RIGHT JOIN show_images ON show_id = id
    """)
    
    for show in shows:

        # if show['img'] and show['slug'] and show['id'] == 175:
        if show['img'] and show['slug'] and '.gif' not in show['img']:
                sizes = json.loads(show['sizes'])
                save_file_base = f"{save_folder_base}{show['slug']}/{show['slug']}"
                dom_colours = find_dominant_img_colours(f"{save_file_base}_{sizes[-1]['w']}.jpg")
            
                mySQL.insert_image(show['id'], show['last_updt'], show['sizes'], json.dumps(dom_colours))
