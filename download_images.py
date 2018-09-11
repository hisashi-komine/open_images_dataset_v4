#!/usr/bin/env python

import argparse
import os
import sqlite3
import requests
from contextlib import closing

from lib import logging, sql, make_image_name
from settings import DATASET, IMAGES_DIR, DATASET_DB, LABELS_DIR


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    if not args.thumb_only:
        os.makedirs(os.path.join(IMAGES_DIR, args.set, 'org'), exist_ok=True)
    if not args.org_only:
        os.makedirs(os.path.join(IMAGES_DIR, args.set, 'thumb'), exist_ok=True)

    os.makedirs(os.path.join(LABELS_DIR, args.set), exist_ok=True)

    with closing(sqlite3.connect(DATASET_DB)) as conn:
        query, params = sql.select_image_urls(
            bboxes_table=DATASET['bboxes'][args.set]['table'],
            labels_table=DATASET['labels'][args.set]['table'],
            images_table=DATASET['images'][args.set]['table'],
            class_names=args.classes,
            limit=args.limit,
            offset=args.offset
        )

        for row in conn.execute(query, params):
            image_id, org_url, thumb_url = row
            create_label = False

            if not args.thumb_only:
                if not org_url:
                    logger.warn(f'[{image_id}:org] Image url is empty')
                    continue

                image_path = os.path.join(
                    IMAGES_DIR,
                    args.set,
                    'org',
                    make_image_name(image_id, org_url)
                )

                if os.path.exists(image_path) and not args.overwrite:
                    logger.info(f'[{args.set}:{image_id}:org] {image_path} already exists')
                    create_label = True
                elif requests.head(org_url).status_code == 302:
                    logger.warn(f'[{args.set}:{image_id}:org] The image is no longer available')
                else:
                    logger.info(
                        f'[{args.set}:{image_id}:org] Downloading image {org_url} -> {image_path}'
                    )
                    response = requests.get(org_url)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    create_label = True

            if not args.org_only:
                if not thumb_url:
                    logger.warn(f'[{image_id}:thumb] Image url is empty')
                    continue

                image_path = os.path.join(
                    IMAGES_DIR,
                    args.set,
                    'thumb',
                    make_image_name(image_id, thumb_url)
                )

                if os.path.exists(image_path) and not args.overwrite:
                    logger.info(f'[{args.set}:{image_id}:thumb] {image_path} already exists')
                    create_label = True
                elif requests.head(org_url).status_code == 302:
                    logger.warn(f'[{args.set}:{image_id}:thumb] The image is no longer available')
                else:
                    logger.info(
                        f'[{args.set}:{image_id}:thumb] '
                        f'Downloading image {thumb_url} -> {image_path}'
                    )
                    response = requests.get(thumb_url)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    create_label = True

            if create_label:
                labels_path = os.path.join(LABELS_DIR, args.set, f'{image_id}.txt')

                if os.path.exists(labels_path) and not args.overwrite:
                    logger.info(f'[{args.set}:{image_id}:label] {labels_path} already exists')
                else:
                    with open(labels_path, 'w') as f:
                        logger.info(f'[{args.set}:{image_id}:label] Writing labels -> {labels_path}')
                        _query, _params = sql.select_labels(
                            bboxes_table=DATASET['bboxes'][args.set]['table'],
                            labels_table=DATASET['labels'][args.set]['table'],
                            image_id=image_id,
                            class_names=args.classes,
                        )
                        for class_name, x, y, width, height in conn.execute(_query, _params):
                            f.write(f'{args.classes.index(class_name)} {x} {y} {width} {height}\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--set',
        type=str,
        default='train',
        choices=['train', 'validation', 'test'],
        help='Set of data (train, validation or test)',
    )
    parser.add_argument(
        '--classes',
        type=str,
        nargs='+',
        help='List of classes to download (e.g. Person "Human eye")',
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
        '--limit',
        type=int,
        help='Limit of the download images num',
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        help='Offset of the download images num',
    )
    parser.add_argument(
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
