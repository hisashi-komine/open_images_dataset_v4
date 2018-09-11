import os

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
PREVIEWS_DIR = os.path.join(BASE_DIR, 'previews')
LABELS_DIR = os.path.join(BASE_DIR, 'labels')

DATASET_DB = os.path.join(BASE_DIR, 'dataset.sqlite')

DATASET = {
    'metadata': {
        'classes': {
            'table': 'classes',
            'local_path': os.path.join(DATASET_DIR, 'class-descriptions-boxable.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/class-descriptions-boxable.csv',
        }
    },
    'bboxes': {
        'train': {
            'table': 'bboxes_train',
            'local_path': os.path.join(DATASET_DIR, 'train-annotations-bbox.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/train/train-annotations-bbox.csv',
        },
        'validation': {
            'table': 'bboxes_validation',
            'local_path': os.path.join(DATASET_DIR, 'validation-annotations-bbox.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/validation/validation-annotations-bbox.csv',
        },
        'test': {
            'table': 'bboxes_test',
            'local_path': os.path.join(DATASET_DIR, 'test-annotations-bbox.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/test/test-annotations-bbox.csv',
        },
    },
    'labels': {
        'train': {
            'table': 'labels_train',
            'local_path': os.path.join(DATASET_DIR, 'train-annotations-human-imagelabels-boxable.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/train/train-annotations-human-imagelabels-boxable.csv',
        },
        'validation': {
            'table': 'labels_validation',
            'local_path': os.path.join(DATASET_DIR, 'validation-annotations-human-imagelabels-boxable.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/validation/validation-annotations-human-imagelabels-boxable.csv',
        },
        'test': {
            'table': 'labels_test',
            'local_path': os.path.join(DATASET_DIR, 'test-annotations-human-imagelabels-boxable.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/test/test-annotations-human-imagelabels-boxable.csv',
        },
    },
    'images': {
        'train': {
            'table': 'images_train',
            'local_path': os.path.join(DATASET_DIR, 'train-images-boxable-with-rotation.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv',
        },
        'validation': {
            'table': 'images_validation',
            'local_path': os.path.join(DATASET_DIR, 'validation-images-with-rotation.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv',
        },
        'test': {
            'table': 'images_test',
            'local_path': os.path.join(DATASET_DIR, 'test-images-with-rotation.csv'),
            'remote_url': 'https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv',
        },
    },
}

BBOX_COLORS = [
    (  0, 255, 255),
    (255,   0, 255),
    (255, 255,   0),
    (255,   0,   0),
    (  0, 255,   0),
    (  0,   0, 255),
]
