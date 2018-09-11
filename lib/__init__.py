import os
import urllib.parse

import requests


def make_image_name(image_id, url):
    return f'{image_id}{os.path.splitext(urllib.parse.urlparse(url).path)[1]}'


def is_url_available(url):
    return url and requests.head(url).status_code != 302
