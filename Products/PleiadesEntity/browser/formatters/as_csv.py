import csv
import json
import os


class Column(object):

    def __init__(self, name, sourceName=None, convert=None):
        self.name = name
        if sourceName is None:
            sourceName = name
        self.sourceName = sourceName
        if convert is not None:
            self.convert = convert

    def get(self, adapter):
        getter = getattr(adapter, self.sourceName)
        value = getter()
        if value is not None:
            return self.convert(value)
        return ''

    def convert(self, value):
        return value


def join_ids_with_comma(v):
    return ','.join(item.getId() for item in v)


def join_with(separator):
    def join(v):
        return separator.join(v)
    return join


def join_initials(values):
    return ''.join(value[0].upper() for value in values)


PLACE_COLUMNS = (
    Column('authors', 'author_names'),
    Column('bbox', convert=lambda v: ', '.join(map(str, v))),
    Column('connectsWith', '_connectsWith', convert=join_ids_with_comma),
    Column('created'),
    Column('creators', convert=lambda v: ', '.join(member.username() or member.name() for member in v)),
    Column('currentVersion', 'current_version'),
    Column('description'),
    Column('extent', convert=json.dumps),
    Column('featureTypes', 'placeTypes', convert=join_with(', ')),
    Column('geoContext'),
    Column('hasConnectionsWith', '_hasConnectionsWith', convert=join_ids_with_comma),
    Column('id'),
    Column('locationPrecision'),
    Column('maxDate', 'end'),
    Column('minDate', 'start'),
    Column('modified'),
    Column('path'),
    Column('reprLat', 'reprPoint', convert=lambda v: str(v[1])),
    Column('reprLatLong', 'reprPoint', convert=lambda v: '{:f},{:f}'.format(v[1], v[0])),
    Column('reprLong', 'reprPoint', convert=lambda v: str(v[0])),
    Column('tags', 'subject', convert=join_with(', ')),
    Column('timePeriods', convert=join_initials),
    Column('timePeriodsKeys', 'timePeriods', convert=join_with(',')),
    Column(
        'timePeriodsRange', 'temporalRange',
        convert=lambda v: '{:.1f},{:.1f}'.format(v[0], v[1])
    ),
    Column('title'),
    Column('uid'),
)


def format_csv(adapter):
    row = []
    for column in PLACE_COLUMNS:
        value = column.get(adapter)
        row.append(value)
    return row


class CSVFormatter(object):

    def __init__(self, path):
        self.filepath = os.path.join(path, 'pleiades-places.csv')

    def start(self):
        self.f = open(self.filepath, 'w')
        self.writer = csv.writer(self.f)
        columns = [column.name for column in PLACE_COLUMNS]
        self.writer.writerow(columns)

    def dump_one(self, adapter):
        row = format_csv(adapter)
        self.writer.writerow(row)

    def finish(self):
        self.f.close()
