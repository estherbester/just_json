from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import urlencode
from jsonstuff.jsondump.models import Entry, Service

import json 
import re

class ServiceFeed():
    def __init__(self, service, user_id, password=None):
      self.service = service
      self.user_id = user_id
#      self.password = password
      if service == "flickr":
         self.url = ('http://api.flickr.com/services/feeds/photos_public.gne?id=%s&format=json&nojsoncallback=1' % user_id)
      elif service == "twitter":
         self.url = ('http://twitter.com/statuses/user_timeline/%s.json?trim_user=true&include_rts=true' % user_id)
      elif service == "youtube":
         self.url = ('http://gdata.youtube.com/feeds/api/users/%s/uploads?v=2&alt=json' % user_id)
         
def getjson(servicefeed):
    response = urlopen(servicefeed.url)
    service = servicefeed.service
    the_json = response.read()
    if service == 'flickr':
      the_json = re.sub(r"\\'","'", the_json)  #flickr escapes single quotes  
    feed = json.loads(the_json)
    if service == "flickr":
        feed_items = feed['items']
    elif service == "twitter":
        feed_items = feed
    elif service == "youtube":
        feed_items = feed['feed']['entry']
    else:
        feed_items = []
    return feed_items 

def save_items(feed, servicefeed):
    feed.reverse() #reverse chronological order
    service = servicefeed.service 
    if len(feed) > 0:
      for f in feed:
        if service == "flickr":
            service_identifier = f['link']
        elif service == "twitter":
            service_identifier =  'http://twitter.com/'+servicefeed.user_id+'/statuses/'+str(f['id'])
        elif service == "youtube":
            service_identifier = f['link'][0]['href']
        else:
            service_identifier = "none"
        
        service_type = Service.objects.get(pk=service)
        post = Entry.objects.get_or_create(service_identifier=service_identifier,raw_json=str(f), service=service_type)

servicefeed = ServiceFeed("twitter", 'estherbester')
feed = getjson(servicefeed)
save_items(feed, servicefeed)
