#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert a iCalendar/ICS file to CSV

The CSV is printed to stdout.

Usage:
  ics_to_csv.py --file <path-to-ics-file> 
  ics_to_csv.py (-h | --help)
  ics_to_csv.py --version

Options:
  -h, --help                  Show this screen.
  --version                   Show version.
  -f, --file <path-to-file>   Path to the ICS file.

"""


from icalendar import Calendar, Event
import csv
import sys
from docopt import docopt
arguments = docopt(__doc__, version='Convert ICS file to CSV 1.0')


def map_event(comp):
    properties = {v[0]: v[1] for v in comp.property_items()}
    del properties['BEGIN']
    del properties['END']

    template = {
        'DTSTART': {
            'prop': 'start_date',
            'fn': lambda x: x.dt,
        },
        'DTEND': {
            'prop': 'end_date',
            'fn': lambda x: x.dt,
        },
        'DTSTAMP': {
            'prop': 'created_date',
            'fn': lambda x: x.dt,
        },
        'SUMMARY': { 
            'prop': 'summary',
            'fn': str,
        },
        'LOCATION': { 
            'prop': 'location',
            'fn': str,
        },
        'DESCRIPTION': { 
            'prop': 'description',
            'fn': str,
        },
        'UID': {
            'prop': 'uid',
            'fn': str,
        },
    }
    event = {'extra': {}}
    for k, v in properties.items():
        if k in template:
            t = template[k]
            event[t['prop']] = t['fn'](v)
        else:
            event['extra'][k] = str(v)
    return event


# parse the ICS file
cal = None
with open(arguments['--file']) as f:
    cal = Calendar.from_ical(f.read())

# convert to CSV/JSON?
events = []
for component in cal.walk(name="VEVENT"):

    # map properties
    event = map_event(component)
    del event['extra']

    events.append(event)


# sort events by date
sorted_events = sorted(events, key=lambda e: e['start_date'])

field_names = ['start_date', 'end_date', 'summary', 'uid', 'created_date']
writer = csv.DictWriter(sys.stdout, field_names,
                        delimiter=',',
                        quotechar='"',
                        lineterminator='\n',
                        quoting=csv.QUOTE_MINIMAL)

writer.writeheader()
writer.writerows(sorted_events)
