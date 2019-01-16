# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import current_app
from google.cloud import datastore
from datetime import datetime, tzinfo, timedelta


class simple_utc(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


builtin_list = list


def init_app(app):
    pass


def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity['_region_id']
    return entity
# [END from_datastore]


# [START list]
def list(limit=10, cursor=None):
    ds = get_client()

    query = ds.query(kind='daily_traffic', order=['_last_updt'])
    query.add_filter('_last_updt', '>=', datetime.utcnow())
    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor
# [END list]


def read(id):
    ds = get_client()
    # key = ds.key('daily_traffic', id)
    # results = ds.get(key)
    # return from_datastore(results)

    query = ds.query(kind='daily_traffic', order=['-_last_updt'])
    query.add_filter('_region_id', '=', id)
    query.add_filter('_last_updt', '>=', datetime.utcnow())
    query_iterator = query.fetch(limit=1)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))

    return entities


def read_gl(id):
    ds = get_client()
    # ql = gql(
        #"SELECT * FROM daily_traffic where _region_id=1 AND _last_updt >= DATETIME('2018-10-22T00:22:57.00002-05:00')"
    # )
    query = ds.query(kind='daily_traffic')
    query.add_filter('_region_id', '=', id)
    query_iterator = query.fetch(limit=1)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))

    return entities


# [START update]
def update(data, id=None):
    ds = get_client()
    if id:
        key = ds.key('daily_traffic', id)
    else:
        key = ds.key('daily_traffic')

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['description'])

    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)


create = update
# [END update]


def delete(id):
    ds = get_client()
    key = ds.key('daily_traffic', id)
    ds.delete(key)
