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

        # classes_tables = [
        #     ('classes', data.CLASSES_CSV),
        # ]
        # for table, data_csv in classes_tables:
        #     logger.info(f'Creating table {table}')
        #     c.executescript(sql.create_table_classes(table))
        #
        #     logger.info(f'Importing classes from {data_csv} to {table}')
        #     with open(data_csv, 'r') as f:
        #         reader = csv.reader(f)
        #         for row in reader:
        #             c.execute(*sql.insert_into_classes(table, row))

        # boxes_tables = [
        #     (data.train.BOXES_TABLE, data.train.BOXES_CSV),
        #     (data.validation.BOXES_TABLE, data.validation.BOXES_CSV),
        #     (data.test.BOXES_TABLE, data.test.BOXES_CSV),
        # ]
        # for table, data_csv in boxes_tables:
        #     logger.info(f'Creating table {table}')
        #     c.executescript(sql.create_table_bboxes(table))
        #
        #     logger.info(f'Importing boxes from {data_csv} to {table}')
        #     with open(data_csv, 'r') as f:
        #         reader = csv.reader(f)
        #         next(reader)
        #         for row in reader:
        #             c.execute(*sql.insert_into_bboxes(table, row))
        #
        # labels_tables = [
        #     (data.train.LABELS_TABLE, data.train.LABELS_CSV),
        #     (data.validation.LABELS_TABLE, data.validation.LABELS_CSV),
        #     (data.test.LABELS_TABLE, data.test.LABELS_CSV),
        # ]
        # for table, data_csv in labels_tables:
        #     logger.info(f'Creating table {table}')
        #     c.executescript(sql.create_table_labels(table))
        #
        #     logger.info(f'Importing labels from {data_csv} to {table}')
        #     with open(data_csv, 'r') as f:
        #         reader = csv.reader(f)
        #         next(reader)
        #         for row in reader:
        #             c.execute(*sql.insert_into_labels(table, row))
        #
        # images_tables = [
        #     (data.train.IMAGES_TABLE, data.train.IMAGES_CSV),
        #     (data.validation.IMAGES_TABLE, data.validation.IMAGES_CSV),
        #     (data.test.IMAGES_TABLE, data.test.IMAGES_CSV),
        # ]
        # for table, data_csv in images_tables:
        #     logger.info(f'Creating table {table}')
        #     c.executescript(sql.create_table_images(table))
        #
        #     logger.info(f'Importing images from {data_csv} to {table}')
        #     with open(data_csv, 'r') as f:
        #         reader = csv.reader(f)
        #         next(reader)
        #         for row in reader:
        #             c.execute(*sql.insert_into_images(table, row))

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
