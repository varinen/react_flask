"""Utils module."""

from sqlalchemy.orm.query import Query
from app import db


def apply_filter(query: Query, model: db.Model, filter: dict):
    if 'field' in filter and 'value' in filter and 'type' in filter:
        if filter['type'] == 'like':
            query.filter(
                getattr(model, filter['field']).like(filter['value']))
        if filter['type'] == 'equal':
            query.filter_by(getattr(model, filter['field'])).in_(
                filter['value'])

    pass
