import json

from flask import jsonify
from flask_restful import marshal
from sqlalchemy import inspect, or_

FILTER_FUNCS = {
    int: lambda attr, value: attr == value,
    str: lambda attr, value: attr.ilike(value),
    'ManyToMany': lambda attr, value: attr.any(id=value),
}


def resolve_field(model, query, field):
    if '.' in field:
        relationship, field = field.split('.', 1)
        obj = inspect(model).relationships[relationship].mapper.class_
        query = query.join(obj)
    else:
        obj = model

    return query, getattr(obj, field)


def base_query(model):
    return model.query


def filter_query(model, query, filter_arg):
    filter_spec = json.loads(filter_arg)
    for key, values in filter_spec.items():
        if not isinstance(values, list):
            values = [values]

        query, attr = resolve_field(model, query, key)
        try:
            attr_type = attr.prop.expression.type.python_type
        except AttributeError:
            attr_type = 'ManyToMany'

        filter_func = FILTER_FUNCS[attr_type]
        query = query.filter(or_(*(filter_func(attr, value) for value in values)))
    return query


def sort_query(model, query, sort_arg):
    ''' Query arg will be a tuple as JSON - e.g. ["name", "DESC"]. '''
    field, order = json.loads(sort_arg)

    query, field_attr = resolve_field(model, query, field)

    if order == 'DESC':
        return query.order_by(field_attr.desc())

    return query.order_by(field_attr.asc())


def splice_query(model, query, splice_arg):
    return json.loads(splice_arg)


def build_response_for_request(model, request, serializer, query=None):
    if not query:
        query = base_query(model)

    if 'filter' in request.args:
        query = filter_query(model, query, request.args['filter'])

    if 'sort' in request.args:
        query = sort_query(model, query, request.args['sort'])

    start = 0
    end = total_length = query.count()

    if 'range' in request.args:
        start, end = splice_query(model, query, request.args['range'])

    resp = jsonify(marshal(query[start:end + 1], serializer))
    resp.headers.extend({
        'Content-Range': f'posts {start}-{end}/{total_length}'
    })

    return resp
