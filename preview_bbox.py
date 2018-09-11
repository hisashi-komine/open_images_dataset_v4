#!/usr/bin/env python

import argparse
import os
import sqlite3
from contextlib import closing

import cv2

from lib import logging, sql
from settings import DATASET, DATASET_DB, BBOX_COLORS


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    image_id = os.path.splitext(os.path.basename(args.image))[0]

    img_bgr = cv2.imread(args.image)
    img_height, img_width, _ = img_bgr.shape

    with closing(sqlite3.connect(DATASET_DB)) as conn:
        query, params = sql.select_labels(
            bboxes_table=DATASET['bboxes'][args.set]['table'],
            labels_table=DATASET['labels'][args.set]['table'],
            image_id=image_id,
            class_names=args.classes,
        )

        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()

    classes = args.classes if args.classes else list(set([r[0] for r in rows]))

    for class_name, x, y, width, height in rows:
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

    cv2.imshow('preview', img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'image',
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
