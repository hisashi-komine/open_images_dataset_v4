#!/usr/bin/env python

import logging

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.INFO)


def getLogger(*args, **kwargs):
    return logging.getLogger(*args, **kwargs)
