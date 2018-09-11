#!/usr/bin/env python

import argparse
import os
import sqlite3
import tempfile
from contextlib import closing

import cv2
import requests

from lib import logging, sql, rotate_bbox, is_url_available
from settings import DATASET, DATASET_DB, BBOX_COLORS


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    image_id = args.image_id

    with closing(sqlite3.connect(DATASET_DB)) as conn:
        cur = conn.cursor()

        query, params = sql.select_images(
            bboxes_table=DATASET['bboxes'][args.set]['table'],
            labels_table=DATASET['labels'][args.set]['table'],
            images_table=DATASET['images'][args.set]['table'],
            image_id=image_id,
        )
        cur.execute(query, params)
        row = cur.fetchone()
        if not row:
            logger.warn(f'[{args.set}:{image_id}] Image not found')
            return

        _, org_url, thumb_url, rotation = row

        query, params = sql.select_labels(
            bboxes_table=DATASET['bboxes'][args.set]['table'],
            labels_table=DATASET['labels'][args.set]['table'],
            image_id=image_id,
            class_names=args.classes,
        )
        cur.execute(query, params)
        labels = cur.fetchall()

    if is_url_available(thumb_url):
        image_url = thumb_url
        image_type = 'thumb'
    elif is_url_available(org_url):
        image_url = org_url
        image_type = 'org'
    else:
        logger.warn(f'[{args.set}:{image_id}] Image unavailable')
        return

    logger.info(f'[{args.set}:{image_id}:{image_type}] Downloading image {image_url}')

    response = requests.get(image_url)
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(response.content)
        img_path = f.name

    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        logger.warn(f'[{args.set}:{image_id}] Invalid image')
        os.remove(img_path)
        return

    img_height, img_width, _ = img_bgr.shape

    os.remove(img_path)

    logger.info(f'[{args.set}:{image_id}:{image_type}] Drawing preview')

    classes = args.classes if args.classes else list(set([r[0] for r in labels]))
    for class_name, x, y, width, height in labels:
        logger.debug(f'[{args.set}:{image_id}:{image_type}] {x} {y} {width} {height} {rotation}')
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

    logger.info(f'[{args.set}:{image_id}:{image_type}] Displaying preview')

    cv2.imshow('preview', img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'image_id',
        type=str,
    )
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
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
