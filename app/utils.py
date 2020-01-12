"""Utils module."""

from flask_sqlalchemy import BaseQuery
from app import db


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
        if filter_['type'] == 'like':
            query = query.filter(
                getattr(model, filter_['column']).like(
                    "%{}%".format(str(filter_['value']))))
        if filter_['type'] == 'eq':
            query = query.filter(getattr(model, filter_['column']) ==
                                 filter_['value'])
        if filter_['type'] == 'geq':
            query = query.filter(
                getattr(model, filter_['column']) >= filter_['value'])
        if filter_['type'] == 'leq':
            query = query.filter(
                getattr(model, filter_['column']) <= filter_['value'])
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

    if order['dir'] == 'desc':
        entities = entities.order_by(
            getattr(entity_class, order['column']).desc())
    else:
        entities = entities.order_by(
            getattr(entity_class, order['column']).asc())

    return entities.paginate(page, per_page, False)
