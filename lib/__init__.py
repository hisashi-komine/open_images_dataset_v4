import os
import urllib.parse

import requests


def make_image_name(image_id, url):
    return '{}{}'.format(image_id, os.path.splitext(urllib.parse.urlparse(url).path)[1])


def is_url_available(url):
    return url and requests.head(url).status_code != 302


def rotate_bbox(x, y, width, height, rotation):
    if rotation == 90:
        return y, 1 - x, height, width
    elif rotation == 180:
        return 1 - x, 1 - y, width, height
    elif rotation == 270:
        return 1 - y, x, height, width
    else:
        return x, y, width, height
