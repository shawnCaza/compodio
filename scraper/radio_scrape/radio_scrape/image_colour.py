import cv2, numpy as np
import colorsys
from sklearn.cluster import KMeans

# finding dominant colour in image
# from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv

def get_colour_frequencies(cluster, centroids):
    """Returns tuple containing (frequency, [r,g,b])"""

    # Get the number of different clusters, create histogram, and normalize
    labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (hist, _) = np.histogram(cluster.labels_, bins = labels)
    hist = hist.astype("float")
    hist /= hist.sum()

    # Group cluster's color and percentage
    colours = [(percent, color) for (percent, color) in zip(hist, centroids)]
    return colours

def convert_to_hex(colours):
    """Converts RGB to hex"""
    for colour in colours:
        rounded_rgb = [int(x) for x in colour[1]]
        hex = "{:02x}{:02x}{:02x}".format(*rounded_rgb)
        yield hex

def find_dominant_colours(image_path, quantity = 3):
    """
        Returns array of dominant colours in an Image sorted from lightest to darkest.
        `image_path` specifies the path to a local image.
        `quantity` specifies the number of colours to return.
        Within the `get_colour_frequencies` function, the frequency of each colour is calulated, but this is not returned by `find_dominant_colours` at present.
    """

    # Load image and convert to a list of pixels
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    reshape = image.reshape((image.shape[0] * image.shape[1], 3))

    # Find and display most dominant colors
    cluster = KMeans(n_clusters=quantity).fit(reshape)
    colours = get_colour_frequencies(cluster, cluster.cluster_centers_)

    # Sort from lightest to darkest 
    colours.sort(reverse=True, key=lambda colour: colorsys.rgb_to_hls(*colour[1])[1])

    dominant_hex_colours = list(convert_to_hex(colours))

    return dominant_hex_colours


if __name__ == '__main__':

    dom_colours = find_dominant_colours('/Users/scaza/Desktop/DJ-medicineman-CIUT-Show-Page.jpeg')
    print(dom_colours)