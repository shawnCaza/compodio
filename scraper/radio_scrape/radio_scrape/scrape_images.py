import time
import os
import json, requests
import pathlib
import math
from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass, field

from PIL import Image, ImageOps
from dotenv import load_dotenv

import image_colour
import scraper_MySQL

"""
    Iterates through all show image urls in the database.
    New, or updated images are downloaded, processed for responsive sizes, 
    their dominant colours are calculated, and the results are saved to the database.
"""


class Show(TypedDict):
    id: int
    slug: str
    image_url: str
    last_updt: datetime


class ImageDimensions(TypedDict):
    w: int
    h: int


@dataclass
class ImageProps:
    base_name: str
    folder: str
    remote_url: str
    remote_modified: datetime | None
    local_modified: datetime | None
    image: Image.Image | None = None
    responsive_widths: set[int] = field(default_factory=set)
    responsive_dimensions: list[ImageDimensions] = field(default_factory=list)

    @property
    def db_modified(self) -> datetime:
        # If server didn't return a last-modified header,
        # we'll use current date as a refernce point for future comparisons.
        return self.remote_modified if self.remote_modified else datetime.now()


def scrape_images():

    load_dotenv()
    shows_image_folder = f"{os.getenv('image_folder')}/shows"
    mySQL = scraper_MySQL.MySQL()
    shows = _all_shows(mySQL)

    for show in shows:
        if not _valid_show_data(show):
            continue

        req = requests.head(show["image_url"], allow_redirects=True)
        if req.status_code >= 400:
            # If the image url is broken, skip the show
            # TODO: at what point do we stop checking repeatedly invalid urls?
            time.sleep(1.5)
            continue

        image_props = ImageProps(
            folder=f"{shows_image_folder}/{show['slug']}",
            remote_url=show["image_url"],
            base_name=show["slug"],
            remote_modified=_modified(req),
            local_modified=show["last_updt"],
        )

        if _needs_update(image_props):

            _save_image_variations(image_props)

            try:
                dom_colours = image_colour.dominant_colours(
                    file_path(image_props, "jpg")
                )
            except Exception as e:
                print(
                    f"Error calculating dominant image colours for show {show['id']}: {e}"
                )
                dom_colours = None

            mySQL.insert_image(
                show["id"],
                image_props.db_modified,
                json.dumps(image_props.responsive_dimensions),
                json.dumps(dom_colours),
                synched=False,
            )

            time.sleep(90)  # To avoid overloading the server with requests

        else:
            time.sleep(1.5)


def _all_shows(mySQL: scraper_MySQL.MySQL) -> list[Show]:

    shows = mySQL.get_query(
        """
        SELECT id, slug, img as image_url, last_updt
        FROM shows
        LEFT JOIN show_images ON show_id = id
    """
    )
    return shows


def _valid_show_data(show: Show) -> bool:
    return bool(show["image_url"] and len(show["image_url"]) and show["slug"])


def _modified(req: requests.Response) -> datetime | None:

    if "last-modified" in req.headers:

        return datetime.strptime(
            req.headers["last-modified"].replace(" GMT", ""), "%a, %d %b %Y %H:%M:%S"
        )


def _needs_update(image_props: ImageProps) -> bool:

    # would be nice to use Etags here, but not all servers were returning them
    remote_modified = image_props.remote_modified
    local_modified = image_props.local_modified

    if local_modified and remote_modified:
        # We have both remote and local modified dates to compare
        needs_updt = True if local_modified < remote_modified else False

    elif remote_modified is None and local_modified:
        # To handle cases where the server doesn't return a last-modified header
        # TODO: add a check to see if the file has changed by comparing file size
        needs_updt = False

    else:
        # Show image has never been downloaded
        needs_updt = True

    return needs_updt


def _save_image_variations(image_props: ImageProps):

    _open_image(image_props)
    _determine_responsive_sizes(image_props)
    _setup_save_folder(image_props)
    _save_standard_images(image_props)
    _save_responsive_sizes(image_props)


def _open_image(image_props: ImageProps) -> None:

    response = requests.get(image_props.remote_url, stream=True)
    response.raw.decode_content = True
    image_props.image = Image.open(response.raw)


def _determine_responsive_sizes(image_props: ImageProps):
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
        {"w": None, "h": 180, "margin": 40},
        {"w": 334, "h": 188, "margin": 24},
        {"w": 386, "h": 218, "margin": 24},
        {"w": 398, "h": 224, "margin": 24},
        {"w": None, "h": 280, "margin": 0},
    ]

    for constraints in image_breakpoint_contraints:

        # margin is applied to image area only when
        # height is proportionally larger than a 16:9 aspect ratio
        margin = (
            constraints["margin"]
            if aspect_ratio < 16 / 9 or constraints["margin"] == 40
            else 0
        )

        # The available width for the image is constrained by the max height and margin
        available_w = math.ceil((constraints["h"] - margin) * aspect_ratio)

        new_w = (
            available_w
            if not constraints["w"] or available_w < constraints["w"]
            else constraints["w"]
        )

        # zdd new_w, as well as retina sized variations, to responsive_widths.
        # Only add a width that's smaller than the original. we're not upscaling.
        for width in [new_w, new_w * 2, new_w * 3]:
            if width < orig_w:
                image_props.responsive_widths.add(width)


def _setup_save_folder(image_props: ImageProps):

    image_folder_path = pathlib.Path(image_props.folder)
    image_folder_path.mkdir(parents=True, exist_ok=True)

    # Clear out any existing files in the folder
    for file in image_folder_path.iterdir():
        file.unlink()


def _save_standard_images(image_props: ImageProps):

    if image_props.image is None:
        raise ValueError("Image not already open.")

    # Correct orientation of image based on exif data
    image_props.image = ImageOps.exif_transpose(image_props.image)
    image_props.image = image_props.image.convert("RGB")

    image_props.image.save(
        file_path(image_props, "webp"), "webp", lossless=0, quality=50
    )

    image_props.image.save(file_path(image_props, "jpg"), "jpeg", optimize=True)


def _save_responsive_sizes(image_props: ImageProps):
    """
    Creates multiple size versions of an image.
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
            file_path(image_props, "jpg", str(new_w)), "jpeg", optimize=True
        )

        resized_image.save(
            file_path(image_props, "webp", str(new_w)), "webp", lossless=0, quality=50
        )

        image_props.responsive_dimensions.append(
            {"w": resized_image.size[0], "h": resized_image.size[1]}
        )


def file_path(image_props: ImageProps, ext: str, suffix: str | None = None) -> str:

    if suffix is not None:
        return f"{image_props.folder}/{image_props.base_name}_{suffix}.{ext}"
    else:
        return f"{image_props.folder}/{image_props.base_name}.{ext}"


if __name__ == "__main__":
    scrape_images()
