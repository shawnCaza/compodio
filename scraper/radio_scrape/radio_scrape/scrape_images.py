import time
import os
import requests
import pathlib
import math
from datetime import datetime
from dataclasses import dataclass, field
from collections.abc import Iterator

from PIL import Image, ImageOps
from dotenv import load_dotenv
from loguru import logger

import image_colour
import scraper_MySQL

"""
    Iterates through all show image urls in the database.
    New, or updated images are downloaded, processed for responsive sizes, 
    their dominant colours are calculated, and the results are saved to the database.
"""

logger.add("logs/radio_scrape.log", format="{time} {level} {message}", level="INFO")


@dataclass
class Show:
    id: int
    image_url: str
    last_updt: datetime
    slug: str

    @property
    def valid_data(self) -> bool:

        return bool(self.image_url and len(self.image_url) and self.slug)


@dataclass
class ImageDimensions:
    w: int
    h: int


@dataclass
class ImageProps:
    req: requests.Response
    base_name: str
    folder: str
    local_modified: datetime | None
    url: str
    show_id: int

    dom_colours: list[str] | None = None
    sizes: list[ImageDimensions] = field(default_factory=list)

    @classmethod
    def from_url(cls, show: Show, shows_image_folder: str) -> "ImageProps":
        req = requests.head(show.image_url, allow_redirects=True)
        return cls(
            req=req,
            base_name=show.slug,
            folder=f"{shows_image_folder}/{show.slug}",
            local_modified=show.last_updt,
            url=show.image_url,
            show_id=show.id,
        )

    @property
    def needs_update(self) -> bool:
        """
        If we have a modified date for an existing local image,
        determine if the remote image is newer.
        return True if the remote image is newer,
        or if the image has never been downloaded.
        """
        # would be nice to use Etags here, but not all servers were returning them
        last_modified = self.last_modified
        local_modified = self.local_modified
        headers = self.req.headers

        if local_modified and "last-modified" in headers:
            # We have both remote and local modified dates to compare
            needs_updt = True if local_modified < last_modified else False

        elif local_modified and "remote_modified" not in headers:
            # To handle cases where the server doesn't return a last-modified header
            # TODO: add an alternative check to see if the file has changed. ex. Comparing file size?
            needs_updt = False

        else:
            # Show image has never been downloaded
            needs_updt = True

        return needs_updt

    @property
    def last_modified(self) -> datetime:
        """
        If server didn't return a last-modified header,
        we'll use current date as a reference point for future comparisons.
        """
        if "last-modified" not in self.req.headers:
            return datetime.now()
        else:
            return datetime.strptime(
                self.req.headers["last-modified"].replace(" GMT", ""),
                "%a, %d %b %Y %H:%M:%S",
            )


@logger.catch
def scrape_images():

    load_dotenv()
    shows_image_folder = f"{os.getenv('IMAGE_PATH')}/shows"
    mySQL = scraper_MySQL.MySQL()
    shows: list[Show] = _all_shows(mySQL)

    for show in shows:

        if not show.valid_data:
            continue

        props = ImageProps.from_url(show, shows_image_folder)

        if not props.needs_update:
            time.sleep(1.5)
            continue

        _process_image(props, mySQL)
        time.sleep(90)  # To avoid overloading the server with requests


def _all_shows(mySQL: scraper_MySQL.MySQL) -> list[Show]:
    """
    Selects data relevant to the image for all shows in the database.
    """
    shows = [Show(**row) for row in mySQL.get_show_images()]
    return shows


def _process_image(props: ImageProps, mySQL: scraper_MySQL.MySQL):
    """
    Saves image url to disk in a series of responsive sizes,
    calculates the dominant colours of the image,
    and saves the results to the database.
    """
    with Image.open(_download_image(props)) as image:

        image = ImageOps.exif_transpose(image)  # Correct orientation
        image = image.convert("RGB")
        _save_image_variations(props, image)

    try:
        props.dom_colours = image_colour.dominant_colours(file_path(props, "jpg"))
    except Exception as e:
        logger.error(
            f"Error calculating dominant image colours for show {props.show_id}: {e}"
        )

    mySQL.insert_image(props)


def _download_image(props: ImageProps) -> bytes:
    response = requests.get(props.url, stream=True)
    response.raw.decode_content = True
    return response.raw


def _save_image_variations(props: ImageProps, image: Image.Image):

    _setup_save_folder(props)
    _save_standard_images(props, image)
    props.sizes = list(_sizes(image))
    _save_responsive_images(props, image)


def _setup_save_folder(props: ImageProps):
    """
    creates a folder for this show's images, and clears out any existing files.
    """
    image_folder_path = pathlib.Path(props.folder)
    image_folder_path.mkdir(parents=True, exist_ok=True)

    # Clear out any existing files in the folder
    for file in image_folder_path.iterdir():
        file.unlink()


def _save_standard_images(props: ImageProps, image: Image.Image):
    """
    Saves a jpg and webp version of the image at the original size.
    """

    image.save(file_path(props, "webp"), "webp", lossless=0, quality=50)

    image.save(file_path(props, "jpg"), "jpeg", optimize=True)


def _sizes(image: Image.Image) -> Iterator[ImageDimensions]:
    """
    Calculates the Width and Height of the image for various responsive breakpoints.
    """

    responsive_widths = set(_responsive_widths(image))

    for new_w in sorted(responsive_widths, reverse=True):

        current_w = image.size[0]
        current_h = image.size[1]

        decrease_percent = new_w / current_w
        new_h = int(current_h * decrease_percent)

        yield ImageDimensions(w=new_w, h=new_h)


def _responsive_widths(image: Image.Image) -> Iterator[int]:
    """
    Because images are often not the same aspect ratio as the responsive image container,
    the image dimensions we need depend on the aspect ratio of the image compared to
    max-heights/widths allowed by css. As such, the values used here to calculate
    the image sizes are coupled with the css max-widths, max-heights, and margins
    values used across various screen sizes.
    """

    orig_w = image.width
    orig_h = image.height
    aspect_ratio = orig_w / orig_h

    # potential image margins, max width, max height for each breakpoint used in css
    image_breakpoint_constraints = [
        (None, 180, 40),
        (334, 188, 24),
        (386, 218, 24),
        (398, 224, 24),
        (None, 280, 0),
    ]

    for max_w, max_h, margin in image_breakpoint_constraints:

        # margin is applied to image area only when
        # height is proportionally larger than a 16:9 aspect ratio
        margin = margin if aspect_ratio < 16 / 9 or margin == 40 else 0

        # The available width for the image is constrained by the max height and margin
        available_w = math.ceil((max_h - margin) * aspect_ratio)

        new_w = available_w if not max_w or available_w < max_w else max_w

        # add new_w, as well as retina sized variations, to responsive_widths.
        # Only add a width that's smaller than the original. we're not upscaling.
        for width in [new_w, new_w * 2, new_w * 3]:
            if width < orig_w:
                yield width


def _save_responsive_images(props: ImageProps, image: Image.Image) -> None:

    for size in props.sizes:

        resized_image = image.resize(size=(size.w, size.h))

        resized_image.save(file_path(props, "jpg", str(size.w)), "jpeg", optimize=True)

        resized_image.save(
            file_path(props, "webp", str(size.w)), "webp", lossless=0, quality=50
        )


def file_path(props: ImageProps, ext: str, suffix: str | None = None) -> str:
    """
    Returns a file path string for the image based on specified extension and suffix(optional).
    """
    if suffix is not None:
        return f"{props.folder}/{props.base_name}_{suffix}.{ext}"
    else:
        return f"{props.folder}/{props.base_name}.{ext}"


if __name__ == "__main__":
    scrape_images()
