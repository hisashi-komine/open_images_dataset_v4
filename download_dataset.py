#!/usr/bin/env python

import argparse
import os

import requests

from lib import logging
from settings import DATASET, DATASET_DIR


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    os.makedirs(os.path.join(DATASET_DIR, 'org'), exist_ok=True)

    for group, dataset in DATASET.items():
        for subgroup, subdataset in dataset.items():
            logger.info(
                f'[{group}:{subgroup}] '
                f'Downloading {subdataset["remote_url"]} -> {subdataset["local_path"]}'
            )

            response = requests.get(subdataset['remote_url'], stream=True)
            with open(subdataset['local_path'], 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
