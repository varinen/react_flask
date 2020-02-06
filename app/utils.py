"""Utils module."""

import datetime
from flask_sqlalchemy import BaseQuery
from app import db


def strip_column_prefix(column):
    """Strip the column prefix ts_."""
    if column.find("ts_") == 0:
        column = column.replace("ts_", "", 1)
    return column


def process_filter_value(filter_):
    """Process filter values: identify timestamps and convert to datetime."""
    value = filter_['value']
    if filter_['column'].find("ts_") == 0:
        value = datetime.datetime.fromtimestamp(value)

    return value


def apply_filter(query: BaseQuery, model: db.Model, filter_: dict):
    """Apply a filter to a query.
    
    Possible filter types are:
    - like - builds a where clause "column like '%column_value%'"
    - eq  - builds a where clause "column = 'column_value'"
    - geq - builds a where clause "column => 'column_value'"
    - leq - builds a where clause "column <= 'column_value'"
    
    The filter has to have three elements:
    - column - name of the column that corresponds to an attribute of the model
    - type - one of the four types described above
    - value - a value to filter the column by.
    """
    if 'column' in filter_ and 'value' in filter_ and 'type' in filter_:
        column = strip_column_prefix(filter_['column'])
        value = process_filter_value(filter_)

        if filter_['type'] == 'like':
            query = query.filter(
                getattr(model, column).like("%{}%".format(str(value))))

        if filter_['type'] == 'eq':
            query = query.filter(getattr(model, column) == value)

        if filter_['type'] == 'geq':
            query = query.filter(getattr(model, column) >= value)

        if filter_['type'] == 'leq':
            query = query.filter(getattr(model, column) <= value)
    return query


def get_entities(entity_class: db.Model, page: int, per_page: int,
                 filters: list = None, order: dict = None):
    """Return a list of entities, paged, filtered, sorted."""
    if filters is None:
        filters = []
    if order is None:
        order = {"column": "id", "dir": "asc"}

    entities = entity_class.query
    for filter_ in filters:
        entities = apply_filter(entities, entity_class, filter_)

    column = order['column']
    if column.find("ts_") == 0:
        column = column.replace("ts_", "", 1)

    if order['dir'] == 'desc':
        entities = entities.order_by(
            getattr(entity_class, column).desc())
    else:
        entities = entities.order_by(
            getattr(entity_class, column).asc())

    entity_length = len(entities.all())
    if entity_length < (page - 1) * per_page + 1:
        page = entity_length // per_page + 1

    return entities.paginate(page, per_page, False)
