#!/usr/bin/python

from creds import ELASTIC_ENDPOINT
from datetime import datetime

import StringIO
import urllib3
import os
import json
import csv
import re

HTTP = urllib3.PoolManager()


def _gen_url(url, payload={}):
    """A wrapper to reliably generate the full URL for both app engine's URL
    fetch and requests' get."""
    param_list = ["%s=%s" % (k, v) for k, v in payload.items()]
    params = '&'.join(param_list)
    return url + '?' + params


def _read_spreadsheet(spreadsheet_key):
    """Accepts a Google spreadsheet key and returns a list of dictionaries
    with column headers as keys and data as values."""
    base = 'https://docs.google.com/spreadsheet/ccc'
    url = _gen_url(base, payload={'key': spreadsheet_key, 'output': 'csv'})

    try:
        from google.appengine.api import urlfetch
        content = urlfetch.fetch(url).content
    except ImportError:
        import requests
        content = requests.get(url).content

    f = StringIO.StringIO(content)
    reader = csv.reader(f, delimiter=',')

    rows = [row for row in reader]
    header = rows[0]
    data = rows[1:]

    return [dict(zip(header, d)) for d in data]


def _date_handler(ds):
    """Accepts a date string in the Deadspin format; ensures that it is an
    acceptable date and returns a standard format.

    Example call:
        >>> _date_handler('4/12/2013')
        '2013-12-04'
    """
    try:
        if ds == '':
            date = None
        else:
            dt = datetime.strptime(ds, '%m/%d/%Y')
            date = datetime.strftime(dt, '%Y-%m-%d')
            if dt.year < 1980:
                date = None
    except Exception:
        date = None
    return date


def _process(dict_entry):
    """Accepts a dictionary entry read directly from the Deadspin google
    spreadsheet and cleans the entry for input into the common database."""
    # City
    if dict_entry["City"] in ['', 'Unkown']:
        city = None
    else:
        city = dict_entry["City"].title()

    # County
    if (dict_entry["County"].lower() in ['', 'unkown', 'n/a']):
        county = None
    else:
        county = dict_entry["County"].title()

    # Victim's Gender
    if dict_entry["Victim's Gender"] == '':
        gender = None
    else:
        gender = dict_entry["Victim's Gender"].lower()

    # Armed or unarmed
    if dict_entry['Armed or Unarmed?'] == '':
        armed = None
    else:
        armed = dict_entry['Armed or Unarmed?'].lower()

    # Race
    if dict_entry['Race'] == '':
        race = None
    else:
        race = dict_entry['Race'].lower()
    if dict_entry['Hispanic or Latino Origin'] == 'Hispanic or Latino origin':
        race = 'hispanic or latino'

    # Victim outcome
    if dict_entry["Hit or Killed?"] == '':
        outcome = None
    else:
        outcome = dict_entry["Hit or Killed?"].lower()

    # Victim name
    if dict_entry["Victim Name"] == '':
        name = None
    else:
        name = dict_entry["Victim Name"].title()

    # Officer names
    if dict_entry["Name of Officer or Officers"] == '':
        officer_names = None
    else:
        officer_names = dict_entry["Name of Officer or Officers"].title()

    # Shootings
    if dict_entry["Shootings"] == '':
        shootings = None
    else:
        shootings = dict_entry["Shootings"].lower()

    # Shootings
    if dict_entry["Source Link"] == '':
        source_url = None
    else:
        source_url = dict_entry["Source Link"]

    # Shots fired
    if dict_entry["Shots Fired"] == '':
        shots_fired = None
    else:
        shots_fired = int(dict_entry["Shots Fired"])

    # Victim's age
    if dict_entry["Victim's Age"] == '':
        age = None
    else:
        age = int(dict_entry["Victim's Age"])

    # Victim's age
    if dict_entry["Summary"] == '':
        summary = None
    else:
        summary = dict_entry["Summary"]
        summary = re.sub('[\n\t]', ' ', summary).strip()

    # State
    if dict_entry["State"] == '':
        state = None
    else:
        state = dict_entry["State"][0:2]

    # Agency
    if (dict_entry["Agency Name"] == '' or dict_entry["Agency Name"] == 'N/A'):
        agency = None
    else:
        agency = dict_entry["Agency Name"].strip()

    # Weapon
    if (dict_entry["Weapon"] in ['unknown', 'N/A', '']):
        weapon = None
    else:
        weapon = dict_entry["Weapon"].lower()
        weapon = re.sub('["]', '', weapon)

    return {
        'city': city,
        'county': county,
        'victim_gender': gender,
        'victim_armed': armed,
        'searched_date': _date_handler(dict_entry['Date Searched']),
        'incident_date': _date_handler(dict_entry['Date of Incident']),
        'victim_race': race,
        'victim_name': name,
        'outcome': outcome,
        'victim_name': name,
        'shootings': shootings,
        'officer_names': officer_names,
        'source_url': source_url,
        'shots_fired': shots_fired,
        'victim_age': age,
        'summary': summary,
        'state': state,
        'agency': agency,
        'weapon': weapon
    }


def _elastic_dump(doc, index='ois', doc_type='incident'):
    """Accepts a document and inserts it into the Elastic Search database at
    the index and doc type.  Returns the status of the insert."""
    url = os.path.join(ELASTIC_ENDPOINT, index, doc_type)
    res = HTTP.urlopen('POST', url, body=json.dumps(doc))
    return res.data


def scrape():
    """Scrapes the Deadspin spreadsheet, formats the documents, and dumps them
    into the common, elasticsearch database.

    TODO: Convert this into an appengine endpoint.
    """
    dicts = _read_spreadsheet('1cEGQ3eAFKpFBVq1k2mZIy5mBPxC6nBTJHzuSWtZQSVw')
    return [_elastic_dump(_process(d)) for d in dicts]
