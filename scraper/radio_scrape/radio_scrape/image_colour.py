from decimal import *
from collections import namedtuple
import cv2, numpy as np
from PIL import Image, ImageChops
import colorsys
from sklearn.cluster import KMeans
from colormath.color_objects import  LabColor, sRGBColor, HSLColor
from colormath.color_conversions import convert_color


# finding avg dominant colours in image
# from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv

# finding border colour from https://stackoverflow.com/questions/10985550/detect-if-an-image-has-a-border-programmatically-return-boolean


def get_colour_frequencies(cluster, centroids):
    """Returns tuple containing (frequency, LAB)"""

    # Get the number of different clusters, create histogram, and normalize
    labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (hist, _) = np.histogram(cluster.labels_, bins = labels)
    hist = hist.astype("float")
    hist /= hist.sum()

    # Group cluster's (percentage, rgb, hex), 
    colours = []
    # define named tuple with fields for percent, rgb, and hex
    ColourDetails = namedtuple('Colour', ('frequency', 'lab'))
    for (percent, color) in zip(hist, centroids):

        # convert color to colormath rgb so we can easily perfrom conversions
        rgb = sRGBColor(*color, is_upscaled=True)
        lab = convert_color(rgb, LabColor)
        # print('rgb', rgb)
        # print('lab', lab)

        # desaturate and lower contrast so bg colours don't compete with image
        labProcessed = decontrast(desaturate(lab))
        # print('labProcessed', labProcessed)

        # add named tuple to colours list with percent, rgb, and hex
        colours.append(ColourDetails(percent,labProcessed))


    

    return colours


def desaturate(lab):
    """
        Desaturates a colour by converting it to hls and then back to rgb.
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
       redduce contrast of a lab colour
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

def find_avg_dominant_colours(image_path, quantity = 3):
    """
        Returns object with list of objects: 
        {
        'freq': decimal reqpresenting frequency at which colour is present in image, 
        'hex': string hex code of colour
        }.
        `image_path` specifies the path to a local image.
        `quantity` specifies the number of colours to return.
        The colour are an average of the dominant clusters of colours. For example, an image with equal amount of red and yellow might return orange.
    """


    # Load image and convert to a list of pixels
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    reshape = image.reshape((image.shape[0] * image.shape[1], 3))

    # Find most dominant colors
    cluster = KMeans(n_clusters=quantity).fit(reshape)
    freq_n_colours = get_colour_frequencies(cluster, cluster.cluster_centers_)

    # Sort from darkest to lightest
    freq_n_colours.sort(reverse=False, key=lambda colour: colour.lab.lab_l)

    dom_hex_colours = [ convert_color(colour.lab, sRGBColor).get_rgb_hex() for colour in freq_n_colours]

    return dom_hex_colours


if __name__ == '__main__':


    import scraper_MySQL
    import time
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

        if len(show['img']) and show['slug'] and show['id'] == 175:
        # if len(show['img']) and show['slug']:


                save_file_base = f"{save_folder_base}{show['slug']}/{show['slug']}"


                dom_colours = find_avg_dominant_colours(f"{save_file_base}.jpg")
                
                
                mySQL.insert_image(show['id'], show['last_updt'], show['sizes'], json.dumps(dom_colours))
