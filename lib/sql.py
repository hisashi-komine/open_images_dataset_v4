def create_table_classes(table):
    return f'''\
create table {table} (
  label_name text,
  class_name text
);
'''


def insert_into_classes(table, params):
    return f'''\
insert into {table} (label_name, class_name) values (?, ?)
''', [
    params[0] if params[0] else None,
    params[1] if params[1] else None,
]


def create_table_bboxes(table):
    return f'''\
create table if not exists {table} (
  image_id text,
  source text,
  label_name text,
  confidence float,
  x_min float,
  x_max float,
  y_min float,
  y_max float,
  is_occluded int,
  is_truncated int,
  is_group_of int,
  is_depiction int,
  is_inside int
);
create index if not exists {table}_image_id on {table}(image_id);
create index if not exists {table}_label_name on {table}(label_name);
create index if not exists {table}_image_id_and_label_name on {table}(image_id, label_name);
'''


def insert_into_bboxes(table, params):
    return f'''\
insert into {table} (
  image_id,
  source,
  label_name,
  confidence,
  x_min,
  x_max,
  y_min,
  y_max,
  is_occluded,
  is_truncated,
  is_group_of,
  is_depiction,
  is_inside
) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    params[0] if params[0] else None,
    params[1] if params[1] else None,
    params[2] if params[2] else None,
    float(params[3]) if params[3] else None,
    float(params[4]) if params[4] else None,
    float(params[5]) if params[5] else None,
    float(params[6]) if params[6] else None,
    float(params[7]) if params[7] else None,
    int(params[8]) if params[8] else None,
    int(params[9]) if params[9] else None,
    int(params[10]) if params[10] else None,
    int(params[11]) if params[11] else None,
    int(params[12]) if params[12] else None,
]


def create_table_labels(table):
    return f'''\
create table if not exists {table} (
  image_id text,
  source text,
  label_name text,
  confidence float
);
create index if not exists {table}_image_id on {table}(image_id);
create index if not exists {table}_source on {table}(source);
create index if not exists {table}_label_name on {table}(label_name);
create index if not exists {table}_confidence on {table}(confidence);
create index if not exists {table}_image_id_and_label_name on {table}(image_id, label_name);
'''


def insert_into_labels(table, params):
    return f'''\
insert into {table} (
  image_id,
  source,
  label_name,
  confidence
) values (?, ?, ?, ?)
''', [
    params[0] if params[0] else None,
    params[1] if params[1] else None,
    params[2] if params[2] else None,
    float(params[3]) if params[3] else None,
]


def create_table_images(table):
    return f'''\
create table if not exists {table} (
  image_id text,
  subset text,
  original_url text,
  original_landing_url text,
  license text,
  author_profile_url text,
  author text,
  title text,
  original_size int,
  original_md5 text,
  thumbnail_300k_url text,
  rotation float
);
create index if not exists {table}_image_id on {table}(image_id);
'''


def insert_into_images(table, params):
    return f'''\
insert into {table} (
  image_id,
  subset,
  original_url,
  original_landing_url,
  license,
  author_profile_url,
  author,
  title,
  original_size,
  original_md5,
  thumbnail_300k_url,
  rotation
) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    params[0] if params[0] else None,
    params[1] if params[1] else None,
    params[2] if params[2] else None,
    params[3] if params[3] else None,
    params[4] if params[4] else None,
    params[5] if params[5] else None,
    params[6] if params[6] else None,
    params[7] if params[7] else None,
    int(params[8]) if params[8] else None,
    params[9] if params[9] else None,
    params[10] if params[10] else None,
    float(params[11]) if params[11] != '' else None,
]


def select_classes():
    return 'select * from classes'


def select_images(
    bboxes_table,
    labels_table,
    images_table,
    image_id=None,
    class_names=None,
    limit=None,
    offset=0
):
    params = []

    where_clause = 'where bboxes.is_group_of = 0 and labels.confidence = 1'
    if image_id:
        where_clause += ' and bboxes.image_id = ?'
        params.append(image_id)
    if class_names:
        where_clause += f" and classes.class_name in ({','.join(['?'] * len(class_names))})"
        params += class_names if class_names else []

    limit_clause = f'limit {limit} offset {offset}' if limit else ''

    return f'''\
select
  distinct bboxes.image_id,
  images.original_url,
  images.thumbnail_300k_url,
  images.rotation
from
  {bboxes_table} as bboxes
  join {labels_table} as labels
    on bboxes.image_id = labels.image_id and bboxes.label_name = labels.label_name
  join {images_table} as images
    on bboxes.image_id = images.image_id
  join classes
    on labels.label_name = classes.label_name
{where_clause}
{limit_clause}
;
''', params


def select_labels(bboxes_table, labels_table, image_id, class_names=None, confidence=1):
    if class_names:
        class_names_cond = f"and classes.class_name in ({','.join(['?'] * len(class_names))})"
    else:
        class_names_cond = ''

    return f'''\
select
  classes.class_name,
  bboxes.x_min + (bboxes.x_max - bboxes.x_min) / 2 as x,
  bboxes.y_min + (bboxes.y_max - bboxes.y_min) / 2 as y,
  (bboxes.x_max - bboxes.x_min) as width,
  (bboxes.y_max - bboxes.y_min) as height
from
  {bboxes_table} as bboxes
  join {labels_table} as labels
    on bboxes.image_id = labels.image_id and bboxes.label_name = labels.label_name
  join classes
    on labels.label_name = classes.label_name
where
  bboxes.image_id = ?
  {class_names_cond}
  and labels.confidence >= ?
  and bboxes.is_group_of = 0
;
''', [image_id, *(class_names if class_names else []), confidence]
