import sys
sys.path.insert(0, 'lib')

import webapp2
import json
import os
from creds import ELASTIC_ENDPOINT

from google.appengine.api import urlfetch


def _search(q, limit, index='ois', doc_type='incident'):
    """Construct the search query from the supplied, full-text query `q`
    search term and the limit for the results.

    TODO: add ability to filter by specified fields.
    """
    url = os.path.join(ELASTIC_ENDPOINT, index, doc_type, '_search')
    raw = urlfetch.fetch(url + '?q=%s&size=%s' % (q, limit))
    es_res = json.loads(raw.content)
    res = [x['_source'] for x in es_res['hits']['hits']]
    return dict(results=res, count=len(res))


class OISSearchHandler(webapp2.RequestHandler):

    def get(self):
        """Writes search results to endpoint"""
        query = self.request.get('query', '*')
        limit = self.request.get('limit', 10)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            json.dumps(_search(query, limit))
        )


class OISCountHandler(webapp2.RequestHandler):

    def get(self, index='ois', doc_type='incident'):
        """Writes search results to endpoint"""
        url = os.path.join(ELASTIC_ENDPOINT, index, doc_type, '_count')
        res = urlfetch.fetch(url)
        count = json.loads(res.content)['count']
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            # TODO: add support for specific categories
            json.dumps(dict(category='all', count=count))
        )


handlers = webapp2.WSGIApplication([
    ('/content', OISSearchHandler),
    ('/_count', OISCountHandler)
], debug=True)
