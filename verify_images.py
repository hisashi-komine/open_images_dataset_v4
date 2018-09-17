#!/usr/bin/env python

import argparse

import cv2

from lib import logging


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    for image_path in args.images:
        print(image_path)
        cv2.imread(image_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'images',
        type=str,
        nargs='+',
    )
    parser.add_argument(
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
