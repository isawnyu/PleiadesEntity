import csv
import simplejson as json
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


def join_with(separator):
    def join(v):
        return separator.join(v)
    return join


def join_initials(values):
    return ''.join(value[0].upper() for value in values)


def sort_columns(columns):
    return tuple(sorted(columns, key=lambda col: col.name))


COMMON_COLUMNS = (
    Column('authors', 'author_names'),
    Column('bbox', convert=lambda v: ', '.join(map(str, v))),
    Column('created'),
    Column('creators', convert=lambda v: ', '.join(member.username() or member.name() for member in v)),
    Column('currentVersion', 'current_version'),
    Column('description'),
    Column('extent', convert=simplejson.dumps),
    Column('featureTypes', 'placeTypes', convert=join_with(', ')),
    Column('geoContext'),
    Column('id'),
    Column('locationPrecision'),
    Column('maxDate', 'end'),
    Column('minDate', 'start'),
    Column('modified'),
    Column('path'),
    Column('reprLat', 'reprPoint', convert=lambda v: str(v[1])),
    Column('reprLatLong', 'reprPoint', convert=lambda v: '{},{}'.format(str(v[1]), str(v[0]))),
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

PLACE_COLUMNS = COMMON_COLUMNS + (
    Column('connectsWith', '_connectsWith', convert=join_with(',')),
    Column('extent', convert=json.dumps),
    Column('featureTypes', 'placeTypes', convert=join_with(', ')),
    Column('geoContext'),
    Column('hasConnectionsWith', '_hasConnectionsWith',
           convert=join_with(',')),
)
PLACE_COLUMNS = sort_columns(PLACE_COLUMNS)


NAME_COLUMNS = COMMON_COLUMNS + (
    Column('pid'),
    Column('nameAttested', 'attested'),
    Column('nameLanguage', 'language'),
    Column('nameTransliterated', 'romanized'),
    Column('extent', convert=json.dumps),
)
NAME_COLUMNS = sort_columns(NAME_COLUMNS)


LOCATION_COLUMNS = COMMON_COLUMNS + (
    Column('pid'),
    Column('geometry', convert=json.dumps),
    Column('featureType', 'featureType', convert=join_with(',')),
)
LOCATION_COLUMNS = sort_columns(LOCATION_COLUMNS)


def format_csv(adapter, columns=PLACE_COLUMNS):
    row = []
    for column in columns:
        value = column.get(adapter)
        if isinstance(value, unicode):
            value = value.encode('utf8')
        row.append(value)
    return row


class CSVFormatter(object):

    filename = 'pleiades-places.csv'
    columns = PLACE_COLUMNS

    def __init__(self, path):
        self.filepath = os.path.join(path, self.filename)

    def start(self):
        self.f = open(self.filepath, 'w')
        self.writer = csv.writer(self.f)
        columns = [column.name for column in self.columns]
        self.writer.writerow(columns)

    def dump_one(self, adapter):
        row = format_csv(adapter, self.columns)
        self.writer.writerow(row)

    def finish(self):
        self.f.close()


class CSVNameFormatter(CSVFormatter):
    filename = 'pleiades-names.csv'
    columns = NAME_COLUMNS


class CSVLocationFormatter(CSVFormatter):
    filename = 'pleiades-locations.csv'
    columns = LOCATION_COLUMNS
