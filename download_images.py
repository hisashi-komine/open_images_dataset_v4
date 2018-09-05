#!/usr/bin/env python

import argparse
import os
import sqlite3
import requests
from contextlib import closing

from lib import logging, sql, make_image_name
from settings import DATASET, IMAGE_DIR, DATASET_DB


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    os.makedirs(os.path.join(IMAGE_DIR, 'org'), exist_ok=True)
    os.makedirs(os.path.join(IMAGE_DIR, 'thumb'), exist_ok=True)

    with closing(sqlite3.connect(DATASET_DB)) as conn:
        query, params = sql.select_image_urls(
            bboxes_table=DATASET['bboxes'][args.group]['table'],
            labels_table=DATASET['labels'][args.group]['table'],
            images_table=DATASET['images'][args.group]['table'],
            class_names=args.classes,
            limit=args.limit
        )

        for row in conn.execute(query, params):
            image_id, org_url, thumb_url = row

            if not args.thumb_only:
                if not org_url:
                    logger.warn(f'[{image_id}:org] Image url is empty')
                    continue

                image_path = os.path.join(IMAGE_DIR, 'org', make_image_name(image_id, org_url))

                if os.path.exists(image_path) and not args.overwrite:
                    logger.info(f'[{image_id}:org] {image_path} already exists')
                elif requests.head(org_url).status_code == 302:
                    logger.warn(f'[{image_id}:org] The image is no longer available')
                else:
                    logger.info(
                        f'[{image_id}:org] Downloading image {org_url} -> {image_path}'
                    )
                    response = requests.get(org_url)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)

            if not args.org_only:
                if not thumb_url:
                    logger.warn(f'[{image_id}:thumb] Image url is empty')
                    continue

                image_path = os.path.join(IMAGE_DIR, 'thumb', make_image_name(image_id, thumb_url))

                if os.path.exists(image_path) and not args.overwrite:
                    logger.info(f'[{image_id}:thumb] {image_path} already exists')
                elif requests.head(org_url).status_code == 302:
                    logger.warn(f'[{image_id}:thumb] The image is no longer available')
                else:
                    logger.info(
                        f'[{image_id}:thumb] Downloading image {thumb_url} -> {image_path}'
                    )
                    response = requests.get(thumb_url)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--group',
        type=str,
        default='train',
        choices=['train', 'validation', 'test'],
        help='Choice of train, validation or test data group',
    )
    parser.add_argument(
        '--classes',
        type=str,
        nargs='+',
        help='List of classes to download (e.g. Person "Human eye")',
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit of the download images num',
    )
    parser.add_argument(
        '--org-only',
        action='store_true',
        help='Download original images only',
    )
    parser.add_argument(
        '--thumb-only',
        action='store_true',
        help='Download thumbnail images only',
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing images',
    )
    parser.add_argument(
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
