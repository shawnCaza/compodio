from decimal import *
from dataclasses import dataclass
from dataclasses import field
import math
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import KMeans
from colormath.color_objects import  LabColor, sRGBColor, HSLColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000 as visual_difference

# The goal of this script is to return a list of distinct hex colours.
# Colours are sorted from darkest to lightest, based on the dominant colours in an image. 
# The intention is to use these colours as a gradient background for the image when displayed on the web page.

# The entry point for this module is the dominant_colours function.


@dataclass(kw_only=True, frozen=True)
class _ClusterColour:
    cluster_size: float # percentage of image pixels in the cluster
    rgb: sRGBColor # the centre colour of the cluster

    @property
    def as_lab(self)-> LabColor:
        return convert_color(self.rgb, LabColor, target_illuminant="d65")

    def as_hex(self)-> str:
        return self.rgb.get_rgb_hex()
    

def dominant_colours(image_path: str, n_clusters: int = 3) -> list[str]:
    """
        param image_path: string path to image file
        param n_clusters: int number - number of cluster colours to look for. Default is 3.
        Returns: list with of hex colours

        k-means clustering is used to cluster n similar colours together, and obtain the mean colour of each group.
        n is specified by the quantity parameter.

        These central colours of each cluster are then processed to obtain results that are more suitable for use as a background gradient behing the image.

        Colours are then filtered for uniqueness, sorted from darkest to lightest, and returned as a list of hex colours.
    """

    image = _read_rgb_image(image_path)

    if image is None:
        # Error reading image. Return empty list so the caller can continue its work.
        return []
    
    # Reshape to a list of pixels.
    # Flatten the 3D array (pixel rows, pixel columns, RGB pixel data) 
    # to 2D (pixels, RGB pixel data)
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # init kmeans - cluster the image data into the specified number of clusters
    clusters = KMeans(n_clusters=n_clusters).fit(image)
    cluster_sizes = _calculate_cluster_sizes(clusters)
    cluster_centers = [_process_colour(sRGBColor(*color, is_upscaled=True)) for color in clusters.cluster_centers_]

    colours = [_ClusterColour(cluster_size=cluster_size, rgb=colour) 
                for (cluster_size, colour) in zip(cluster_sizes, cluster_centers)
              ]

    colours = _remove_similar_colours(colours)
    # Sort from darkest to lightest based on lab L* value
    colours.sort(reverse=False, key=lambda colour: colour.as_lab.lab_l)

    return [colour.as_hex() for colour in colours]

def _read_rgb_image(image_path: str) -> NDArray[Any, np.uint8]:
    # Load image and convert to numpy array of pixels data
    # Largely borrowed from https://stackoverflow.com/a/58177484

    image_BGR = cv2.imread(image_path)

    if image_BGR is None:
        print (f"Error: Could not read image at {image_path}")
        return

    image_RGB = cv2.cvtColor(image_BGR, cv2.COLOR_BGR2RGB)
    return image_RGB

def _2d_image(image: NDArray[NDArray[np.uint8]]) -> NDArray[np.uint8]:
    """
        Converts a 3D array of image data (pixel rows, pixel columns, RGB pixel data) 
        to 2D (pixels, RGB pixel data)
    """ 
    image = image.reshape((image.shape[0] * image.shape[1], 3))
    return image.reshape((image.shape[0] * image.shape[1], 3))

def _calculate_cluster_sizes(clusters: KMeans) -> list[float]:
    """Returns the size of each cluster as a percentage of the total number of pixels in the image."""

    # Generate a range of integers from 0 to the number of unique cluster labels (inclusive). 
    labels = np.arange(0, len(np.unique(clusters.labels_)) + 1)
    #histogram will give us the number of pixels for each cluster
    (cluster_pixel_counts, _) = np.histogram(clusters.labels_, bins = labels)
     
    # Normalize the histogram - divide by the total number of pixels to get the percentage of pixels in each cluster
    cluster_pixel_counts_float = cluster_pixel_counts.astype("float")
    cluster_size = cluster_pixel_counts_float / cluster_pixel_counts_float.sum()
    
    return cluster_size

def _process_colour(rgb:sRGBColor) -> sRGBColor:
    """
        Processes a colour so it competes less with source image when used behind the image.
    """

    def _desaturate():
        """
            # Desaturate a little more the higher the original saturation is.
            # Saturation values can range from 0 to 1
            # We are curving this range down to sat_limit
        """
        nonlocal rgb
        
        sat_limit = 0.65
        sat_upper_range = 1

        hsl = convert_color(rgb, HSLColor)
        sat = hsl.hsl_s
        sat = sat - ((sat * (sat_upper_range - sat_limit)) * (sat / sat_upper_range))
        hsl.hsl_s = sat

        rgb = convert_color(hsl, sRGBColor)


    def _decontrast():
        """
            Converts rgb to lab
            then remaps the L* values range of 0 to 100 to a linear scale between min_l and max_l
        """

        nonlocal rgb
        lab = convert_color(rgb, LabColor, target_illuminant="d65")
        
        min_l = 15
        max_l = 85
        
        # Remap the L* value to a linear scale between min_l and max_l
        # This will make the colour appear less contrasty when used as a background.
        # The min_l and max_l values are chosen to give a good result when used as a background gradient.
        lab.lab_l = min_l + lab.lab_l * (max_l - min_l) / 100
   
        rgb = convert_color(lab, sRGBColor)

    _desaturate()
    _decontrast() 

    return rgb

def _remove_similar_colours(colours: list[_ClusterColour], min_delta:int=14) -> list[_ClusterColour]:
    """
        Filters out colours that are too similar to each other.
        Prefering the colour appearing more often in the image (from a larger cluster size).
        Colours are considered too similar if the delta E is less than min_delta.

        returns list of filtered CentralClusterColour sorted in descending order by cluster size.
    """
    filtered:_ClusterColour = []
    colours.sort(reverse=True, key=lambda colour: colour.cluster_size)
    for c in colours:
        if not any(visual_difference(c.as_lab, f.as_lab) < min_delta for f in filtered):
            filtered.append(c)

    return filtered


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

        # if show['img'] and show['slug'] and show['id'] == 146152:
        if show['img'] and show['slug']:
            sizes = json.loads(show['sizes'])
            save_file_base = f"{save_folder_base}{show['slug']}/{show['slug']}"
            dom_colours = dominant_colours(f"{save_file_base}_{sizes[-1]['w']}.jpg")
        
            mySQL.insert_image(show['id'], show['last_updt'], show['sizes'], json.dumps(dom_colours))