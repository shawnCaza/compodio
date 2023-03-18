from decimal import *

import cv2, numpy as np
from PIL import Image, ImageChops
import colorsys
from sklearn.cluster import KMeans

# finding avg dominant colours in image
# from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv

# finding border colour from https://stackoverflow.com/questions/10985550/detect-if-an-image-has-a-border-programmatically-return-boolean

def is_there_a_border(image_path):
    with Image.open(image_path).convert('RGB') as im:

        corner_pixel = im.getpixel((0,0))

        bg = Image.new(im.mode, im.size, corner_pixel)
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        corner_rgb = [value for value in corner_pixel]
        print(corner_rgb)
        corner_hex = convert_to_hex([value for value in corner_rgb])
        
    return all((bbox[0], bbox[1], (bbox[0] + bbox[2]) <= im.size[0], (bbox[1] + bbox[3]) <= im.size[1])), corner_hex


def get_colour_frequencies(cluster, centroids):
    """Returns tuple containing (frequency, RGB, hex colour)"""

    # Get the number of different clusters, create histogram, and normalize
    labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (hist, _) = np.histogram(cluster.labels_, bins = labels)
    hist = hist.astype("float")
    hist /= hist.sum()

    # Group cluster's (percentage, rgb, hex), 
    # filter out very light colours (hls[1] > 235) and dark colours (hls[1] < 20)
    # desaturate colours
    colours = [(percent, color, convert_to_hex(desaturate(color))) for (percent, color) in zip(hist, centroids) if colorsys.rgb_to_hls(*color)[1] > 20 and colorsys.rgb_to_hls(*color)[1] < 235]
    return colours

def convert_to_hex(rgb_colour_value):
    """
        Converts a list of RGB values to a hex value. 
     
    """
    rounded_rgb = [int(x) for x in rgb_colour_value]
    hex = "{:02x}{:02x}{:02x}".format(*rounded_rgb)
    return hex

def desaturate(rgb_colour_value):
    """
        Desaturates a colour by converting it to hls and then back to rgb.
    """
    hls = colorsys.rgb_to_hls(*rgb_colour_value)
    rgb = colorsys.hls_to_rgb(hls[0], hls[1], hls[2]*.66)
    return rgb

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

    # Doesn't always seem to work. When it does, corner image might not be most representative pixel. I some cases images need to be trimmed.
    # has_solid_border, potential_border_hex_colour = is_there_a_border(image_path)
    # print('solid border?', has_solid_border, potential_border_hex_colour)

    # Load image and convert to a list of pixels
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    reshape = image.reshape((image.shape[0] * image.shape[1], 3))

    # Find most dominant colors
    cluster = KMeans(n_clusters=quantity).fit(reshape)
    freq_n_colours = get_colour_frequencies(cluster, cluster.cluster_centers_)
    # print('freq_n_colours', freq_n_colours)

    # Sort from lightest to darkest 
    freq_n_colours.sort(reverse=True, key=lambda colour: colorsys.rgb_to_hls(*colour[1])[1])

    

    # freq_n_hex = [{'freq': round(Decimal(freq_hex[0]),2), 'hex': freq_hex[2]} for freq_hex in freq_n_colours]
    dom_hex_colours = [ colour[2] for colour in freq_n_colours]

    return dom_hex_colours


if __name__ == '__main__':

    dom_colours = find_avg_dominant_colours('/Users/scaza/Desktop/t3.jpeg')
    print(dom_colours)