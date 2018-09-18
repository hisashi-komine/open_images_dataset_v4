#!/usr/bin/env python

import argparse
import csv
import os
import shutil

from lib import logging


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    images_dir = os.path.join(args.output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    labels_dir = os.path.join(args.output_dir, 'labels')
    os.makedirs(labels_dir, exist_ok=True)

    logger.info('Extract classes {} from {}'.format(args.extract_class_nos, args.images_list))
    with open(args.images_list, 'r') as f:
        for image_path in f.readlines():
            image_path = image_path.rstrip('\n')
            label_path = os.path.join(
                os.path.dirname(image_path.replace('/images/', '/labels/')),
                os.path.splitext(os.path.basename(image_path))[0] + '.txt'
            )

            labels = []
            with open(label_path, 'r') as _f:
                reader = csv.reader(_f, delimiter=" ")
                for row in reader:
                    if int(row[0]) in args.extract_class_nos:
                        labels.append([args.extract_class_nos.index(int(row[0])), *row[1:5]])

            if labels:
                logger.info('Found labels on {}'.format(os.path.basename(image_path)))

                image_dst_path = os.path.join(images_dir, os.path.basename(image_path))
                label_dst_path = os.path.join(labels_dir, os.path.basename(label_path))

                logger.info('Copy image {} -> {}'.format(image_path, image_dst_path))
                shutil.copyfile(image_path, image_dst_path)

                logger.info('Write labels -> {}'.format(label_path))
                with open(label_dst_path, 'w') as _f:
                    writer = csv.writer(_f, delimiter=" ")
                    writer.writerows(labels)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'images_list',
        type=str,
    )
    parser.add_argument(
        'output_dir',
        type=str,
    )
    parser.add_argument(
        '--extract_class_nos',
        type=int,
        nargs='+',
        required=True,
    )
    parser.add_argument(
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
