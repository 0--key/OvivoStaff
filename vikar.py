import os, logging, md5
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import datastore
from google.appengine.ext import db
from models import Company
from google.appengine.api import memcache
from review import get_companies_data, get_unique_tags
import webapp2

def doRender(handler, tname='index.htm', values={}):
    temp = os.path.join('', 'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    newval = dict(values)
    newval['path'] = handler.request.path
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True


class BrowseHandler(webapp2.RequestHandler):
    def get(self, raw_city):
        city = self.request.path_info.split('/')[-1].decode('utf8')
        if raw_city:
            query_str = "SELECT * FROM Company WHERE city='%s'" % city
        else:
            query_str = "SELECT * FROM Company WHERE city='Aabybro'"
        # lets try to memcache the polular pages:
        cache_key = md5.new(query_str.encode('ascii', 'ignore')).hexdigest()
        if memcache.get(key=cache_key):
            companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = memcache.get(key=cache_key)
            logging.info("Cache works perfectly!")
        else:
            companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = get_companies_data(query_str)
            memcache.set(key=cache_key, value=get_companies_data(query_str), time=3600)
        template_values = {'companies':companies_data, 'results_number':results_number, 'cities_first_letters':first_letters_list, 'cities':unique_cities, 'cities_ordered':cities_ordered, 'search_navbar':navbar, 'category':city, 'tags':get_unique_tags()}
        doRender(self,'vikarbureau_restyled.htm', template_values)

application = webapp.WSGIApplication([(r'/vikarbureau/(.*)', BrowseHandler),], debug=True)
