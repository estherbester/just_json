from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import urlencode
from jsonstuff.jsondump.models import *
import datetime
import time
import re
import json 


UN = {'youtube':'estherbester','twitter':'estherbester', 'flickr': '69169589@N00', 'mefi':'estherbester', 'greader':None}

#shamelessly copied from ericflo's django-couch-lifestream app https://github.com/ericflo/django-couch-lifestream  -- well, ok, there was a little shame =P

def parse_json(url, service, callback, discriminator='id', list_key=None):
    print "Fetching %s items" % (service,)
    
    service_name = Service.objects.get(pk=service)
    fetched = urlopen(url).read()
    #fetched = open('jsondump/flickr.json','r').read()
    if service == 'flickr':
        fetched = re.sub(r"\\'","'",fetched) #stupid flickr, need to remove escaped apostrophes
    data = json.loads(fetched)
    if list_key:
        data = data[list_key]
    for item in map(callback, data):        
        try:
           post = Entry.objects.get(service_identifier=item[discriminator])
        except:
          post = Entry.objects.create(service_identifier=item[discriminator],raw_json=item, service=service_name,)
    print "%s items fetched" % (service,)

def parse_feed(url, service, discriminator='id'):
    import feedparser
    print "Fetching %s items" % (service,)
    d = feedparser.parse(url)
#    d = open('jsondump/mefi.feed', 'r').read()
    for item in map(dict, d['entries']):
        item['entry_date'] = datetime.datetime.fromtimestamp(
            time.mktime(item['updated_parsed']))
        entry_date = item['entry_date']
        try:
          post = Entry.objects.get(service_identifier=item[discriminator])
        except:
              for (key, val) in item.items():
                    if 'parsed' in key:
                        del item[key]
                    elif isinstance(val, datetime.datetime):
                        item[key] = val.isoformat()
                    elif isinstance(val, datetime.date):
                        item[key] = val.isoformat()
              service = Service.objects.get(pk=service)
              post = Entry.objects.create(service_identifier=item[discriminator],raw_json=item, service=service, entry_date=entry_date)
    print "%s items fetched" % (service,)

def fetch_twitter_items(username):
    from dateutil.parser import parse
    def callback(item):
        item['entry_date'] = parse(item['created_at']).isoformat()  #adds entry_date item to existing json item
        return item
    url = 'http://twitter.com/statuses/user_timeline/%s.json?trim_user=true&include_rts=true' % username
    faves_url = 'http://api.twitter.com/1/favorites/%s.json' % username
    parse_json(url, 'twitter', callback )

def fetch_flickr_items(username):
    uploads_url = 'http://api.flickr.com/services/feeds/photos_public.gne?id=%s&format=json&nojsoncallback=1' % username
    fave_url = 'http://api.flickr.com/services/feeds/photos_faves.gne?id=%s&format=json' % username
    parse_json(uploads_url,'flickr', None, 'link','items')

def fetch_youtube_items(username):
    yt_url = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?v=2&alt=atom' % username
    yt_faves_url = 'http://gdata.youtube.com/feeds/api/users/%s/favorites?v=2&alt=atom' % username
    parse_feed(yt_url, 'youtube', 'link')  #needs a better discriminator

if Service.objects.all():
  pass
else:
  for item in SERVICES:
    Service.objects.create(service=item[0])

fetch_youtube_items(UN['youtube']) #3x per day

fetch_flickr_items(UN['flickr'])
fetch_twitter_items(UN['twitter'])
