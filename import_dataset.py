#!/usr/bin/env python
import argparse
import csv
import os
import sqlite3
from contextlib import closing

from lib import sql
from lib import logging
from settings import DATASET, DATASET_DB


def main(args):
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    try:
        os.remove(DATASET_DB)
    except OSError:
        pass

    with closing(sqlite3.connect(DATASET_DB)) as conn:
        c = conn.cursor()

        # Import metadata:classes
        ref = DATASET['metadata']['classes']
        logger.info(f'Creating table {ref["table"]}')
        c.executescript(sql.create_table_classes(ref["table"]))

        logger.info(f'Importing classes from {ref["local_path"]} to {ref["table"]}')
        with open(ref["local_path"], 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                c.execute(*sql.insert_into_classes(ref["table"], row))

        # Import bboxes
        for ref in DATASET['bboxes'].values():
            logger.info(f'Creating table {ref["table"]}')
            c.executescript(sql.create_table_bboxes(ref["table"]))

            logger.info(f'Importing from {ref["local_path"]} to {ref["table"]}')
            with open(ref["local_path"], 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    c.execute(*sql.insert_into_bboxes(ref["table"], row))

        # Import labels
        for ref in DATASET['labels'].values():
            logger.info(f'Creating table {ref["table"]}')
            c.executescript(sql.create_table_labels(ref["table"]))

            logger.info(f'Importing from {ref["local_path"]} to {ref["table"]}')
            with open(ref["local_path"], 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    c.execute(*sql.insert_into_labels(ref["table"], row))

        # Import images
        for ref in DATASET['images'].values():
            logger.info(f'Creating table {ref["table"]}')
            c.executescript(sql.create_table_images(ref["table"]))

            logger.info(f'Importing from {ref["local_path"]} to {ref["table"]}')
            with open(ref["local_path"], 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    c.execute(*sql.insert_into_images(ref["table"], row))

        conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--loglevel',
        type=str.upper,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO',
    )

    main(parser.parse_args())
