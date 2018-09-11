#!/usr/bin/env python

import argparse
import cv2
import os
import sqlite3
import requests
from contextlib import closing

from lib import logging, sql, make_image_name, is_url_available, rotate_bbox
from settings import DATASET, IMAGES_DIR, DATASET_DB, LABELS_DIR, BBOX_COLORS, PREVIEWS_DIR


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    images_dir = os.path.join(IMAGES_DIR, args.set)
    os.makedirs(images_dir, exist_ok=True)

    labels_dir = os.path.join(LABELS_DIR, args.set)
    os.makedirs(labels_dir, exist_ok=True)

    previews_dir = os.path.join(PREVIEWS_DIR, args.set)
    if not args.without_preview:
        os.makedirs(previews_dir, exist_ok=True)

    with closing(sqlite3.connect(DATASET_DB)) as conn:
        cur = conn.cursor()

        if args.classes:
            classes = args.classes
        else:
            cur.execute(sql.select_classes())
            classes = [c[1] for c in cur.fetchall()]

        query, params = sql.select_images(
            bboxes_table=DATASET['bboxes'][args.set]['table'],
            labels_table=DATASET['labels'][args.set]['table'],
            images_table=DATASET['images'][args.set]['table'],
            class_names=args.classes,
            limit=args.limit,
            offset=args.offset
        )
        for row in conn.execute(query, params):
            image_id, org_url, thumb_url, rotation = row

            if is_url_available(thumb_url):
                image_path = os.path.join(images_dir, make_image_name(image_id, thumb_url))
                image_url = thumb_url
                image_type = 'thumb'
            elif is_url_available(org_url):
                image_path = os.path.join(images_dir, make_image_name(image_id, org_url))
                image_url = org_url
                image_type = 'org'
            else:
                logger.warn(f'[{args.set}:{image_id}] Image unavailable')
                continue

            if os.path.exists(image_path) and not args.overwrite:
                logger.info(f'[{args.set}:{image_id}:{image_type}] {image_path} already exists')
            else:
                logger.info(
                    f'[{args.set}:{image_id}:{image_type}] '
                    f'Downloading image {image_url} -> {image_path}'
                )
                response = requests.get(image_url)
                with open(image_path, 'wb') as f:
                    f.write(response.content)

            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                logger.warn(f'[{args.set}:{image_id}] Invalid image')
                os.remove(image_path)
                continue

            labels = []
            labels_path = os.path.join(labels_dir, f'{image_id}.txt')
            if os.path.exists(labels_path) and not args.overwrite:
                logger.info(f'[{args.set}:{image_id}:label] {labels_path} already exists')
            else:
                logger.info(f'[{args.set}:{image_id}:label] Writing labels -> {labels_path}')
                _query, _params = sql.select_labels(
                    bboxes_table=DATASET['bboxes'][args.set]['table'],
                    labels_table=DATASET['labels'][args.set]['table'],
                    image_id=image_id,
                    class_names=args.classes,
                )
                cur.execute(_query, _params)
                labels = cur.fetchall()

                with open(labels_path, 'w') as f:
                    for class_name, x, y, width, height in labels:
                        x, y, width, height = rotate_bbox(x, y, width, height, rotation)
                        f.write(f'{classes.index(class_name)} {x} {y} {width} {height}\n')

            if not args.without_preview:
                preview_path = os.path.join(previews_dir, os.path.basename(image_path))
                if os.path.exists(preview_path) and not args.overwrite:
                    logger.info(f'[{args.set}:{image_id}:preview] {preview_path} already exists')
                else:
                    logger.info(f'[{args.set}:{image_id}:preview] Drawing preview -> {preview_path}')
                    img_height, img_width, _ = img_bgr.shape
                    for class_name, x, y, width, height in labels:
                        logger.debug(
                            f'[{args.set}:{image_id}:{image_type}] '
                            f'{x} {y} {width} {height} {rotation}'
                        )
                        x, y, width, height = rotate_bbox(x, y, width, height, rotation)

                        left = int((x - width / 2) * img_width)
                        right = int((x + width / 2) * img_width)
                        top = int((y - height / 2) * img_height)
                        bottom = int((y + height / 2) * img_height)
                        color = BBOX_COLORS[classes.index(class_name) % len(BBOX_COLORS)]

                        cv2.rectangle(img_bgr, (left, top), (right, bottom), color, 1)
                        cv2.putText(
                            img_bgr,
                            class_name,
                            (left, top + 12),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            .5,
                            color,
                            lineType=cv2.LINE_AA
                        )

                    cv2.imwrite(preview_path, img_bgr)


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
        '--overwrite',
        action='store_true',
        help='Overwrite existing images',
    )
    parser.add_argument(
        '--without-preview',
        action='store_true',
        help='Without bbox preview',
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
