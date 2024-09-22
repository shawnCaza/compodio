from decimal import *
from collections import namedtuple
import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageChops
import colorsys
from sklearn.cluster import KMeans
from colormath.color_objects import  LabColor, sRGBColor, HSLColor
from colormath.color_conversions import convert_color

# finding avg dominant colours in image
# from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv

# finding border colour from https://stackoverflow.com/questions/10985550/detect-if-an-image-has-a-border-programmatically-return-boolean


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

    # NOTE: We're not making use of the frequency of colours from each cluster, but have captured it here for potential future use.
    central_cluster_colours_RGB_and_frequencies = group_cluster_colour_and_frequency(clusters)
    
    processed_colours_RGB = process_colours(central_cluster_colours_RGB_and_frequencies)
    
    # Sort from darkest to lightest
    # central_rgb_colours_and_frequencies.sort(reverse=False, key=lambda colour: colour.lab.lab_l)

    # dom_hex_colours = [ convert_color(colour.lab, sRGBColor).get_rgb_hex() for colour in central_rgb_colours_and_frequencies]

    return dom_hex_colours

def rgb_2d_pixel_array_from_image(image_path: str) -> NDArray[np.uint8]:
    
    # Load image and convert to numpy array of pixels data
    image_data_BGR_3d = cv2.imread(image_path)
    image_data_RGB_3d = cv2.cvtColor(image_data_BGR_3d, cv2.COLOR_BGR2RGB)
    # Reshape to a list of pixels - Flatten the 3D array (pixel rows, pixel columns, RGB pixel data) to 2D (pixels, RGB pixel data)
    image_data_RGB_2d = image_data_RGB_3d.reshape((image_data_RGB_3d.shape[0] * image_data_RGB_3d.shape[1], 3))
    return image_data_RGB_2d

def group_cluster_colour_and_frequency(clusters: KMeans) -> list[tuple[float, sRGBColor]]:
    """Returns list of named tuples containing (frequency, colorMath sRGBColor))"""

    # Generate a range of integers from 0 to the number of unique cluster labels (inclusive). 
    labels = np.arange(0, len(np.unique(clusters.labels_)) + 1)
    #histogram will give us the number of pixels for each cluster
    (cluster_pixel_counts, _) = np.histogram(clusters.labels_, bins = labels)
     
    # Normalize the histogram - divide by the total number of pixels to get the percentage of pixels in each cluster
    cluster_pixel_counts_float = cluster_pixel_counts.astype("float")
    cluster_frequencies = cluster_pixel_counts_float / cluster_pixel_counts_float.sum()

    # Group frequency of each cluster group, to the central colour of that cluster and then add it to the colours list
    central_rgb_colours_and_frequencies = []
    ColourDetails = namedtuple('Colour', ('frequency', 'rgb'))
    for (frequency, color) in zip(cluster_frequencies, clusters.cluster_centers_):

        # convert color to colormath rgb so we can easily perfrom conversions
        rgb = sRGBColor(*color, is_upscaled=True)


        central_rgb_colours_and_frequencies.append(ColourDetails(frequency, rgb))

    return central_rgb_colours_and_frequencies

def process_colours(central_rgb_colours_and_frequencies: list[tuple[float, sRGBColor]]) -> list[sRGBColor]:
    """
        Process the colours to make them more suitable for use as a background gradient behind the image.
        We don't want the background colours to compete with the image, so we desaturate and limit potential dynamic range(very bright colours are dimmed and very dark colours are brightened).
    """
    processed_colours = []
    for colour in central_rgb_colours_and_frequencies:
        lab = convert_color(colour.rgb, LabColor)
        # desaturate and lower contrast so bg colours don't compete with image
        labProcessed = decontrast(desaturate(lab))
        processed_colours.append(convert_color(labProcessed, sRGBColor))
    return processed_colours

def desaturate(lab):
    """
        Desaturates a colour by converting it to hls and then back to lab.
    """

    # convert lab to hsl 
    hsl = convert_color(lab, HSLColor)
    
    # desaturate a little more the more saturated it is
    hsl.hsl_s = hsl.hsl_s - ((hsl.hsl_s * 0.25) + (hsl.hsl_s / 65) * 5)

    # convert back to lab
    lab = convert_color(hsl, LabColor)

    return lab

def decontrast(lab):
    """
        redduces contrast of a lab colour.
        param lab: lab colour
        returns: lab colour
    """

    if lab.lab_l > 60:
        # Too bright, reduce brightness. The brighter the more we reduce
        lab.lab_l = 60 + ((lab.lab_l - 60) * 0.4 )
    elif lab.lab_l < 20:
        # Too dark, increase brightness. The darker the more we increase

        # Make sure L is not less than 1 or crazy things happen in the next step
        lab.lab_l = lab.lab_l if lab.lab_l > 1 else 1
        # Make L at least ten, plus a bit more based on how dark it is
        lab.lab_l = 10 + (lab.lab_l * 0.5 ) + 20 / lab.lab_l * .15
    return lab




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

    folders_to_sync_list = [] # scraped images will be synched to remote server after being processed locally
    
    for show in shows:

        if show['img'] and show['slug'] and show['id'] == 175:
        # if len(show['img']) and show['slug']:


                save_file_base = f"{save_folder_base}{show['slug']}/{show['slug']}"


                dom_colours = find_dominant_img_colours(f"{save_file_base}.jpg")
                
                
                mySQL.insert_image(show['id'], show['last_updt'], show['sizes'], json.dumps(dom_colours))
