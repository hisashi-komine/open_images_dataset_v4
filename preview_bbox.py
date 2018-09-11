#!/usr/bin/env python

import argparse
import os
import sqlite3
from contextlib import closing

import cv2

from lib import logging, sql
from settings import DATASET, DATASET_DB


BBOX_COLORS = [
    (255,   0,   0),
    (  0, 255,   0),
    (  0,   0, 255),
    (  0, 255, 255),
    (255,   0, 255),
    (255, 255,   0),
]


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    image_id = os.path.splitext(os.path.basename(args.image))[0]

    img_bgr = cv2.imread(args.image)

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

    classes = list(set([r[0] for r in rows]))

    for class_name, x, y, width, height in rows:
        cv2.rectangle(
            img_bgr,
            (int((x - width / 2) * img_bgr.shape[1]), int((y - height / 2) * img_bgr.shape[0])),
            (int((x + width / 2) * img_bgr.shape[1]), int((y + height / 2) * img_bgr.shape[0])),
            BBOX_COLORS[classes.index(class_name) % len(BBOX_COLORS)],
            1
        )

    for i, class_name in enumerate(classes):
        cv2.putText(
            img_bgr,
            class_name,
            (0, (i + 1) * 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            thickness=2
        )
        cv2.putText(
            img_bgr,
            class_name,
            (0, (i + 1) * 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            BBOX_COLORS[i % len(BBOX_COLORS)]
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
