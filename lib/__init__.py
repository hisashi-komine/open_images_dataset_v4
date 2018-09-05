import os
import urllib.parse


def make_image_name(image_id, url):
    return f'{image_id}{os.path.splitext(urllib.parse.urlparse(url).path)[1]}'
