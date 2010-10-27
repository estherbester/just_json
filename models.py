from django.db import models
from datetime import datetime


# Create your models here.

SERVICES = (
('flickr', "Flickr"),
('twitter', "Twitter"),
('youtube', "YouTube"),
('tumblr', "Tumblr"),
)

#probably don't need to use this model too often, once you've got the core services entered that you plan to stream
class Service(models.Model):
    service = models.CharField(primary_key=True,choices=SERVICES, max_length=250)
    date_added = models.DateTimeField(default=datetime.now)
    service_user_id = models.CharField(null=True,blank=True, max_length=200)
    
    def __unicode__(self):
      if self.service:
        return self.service

class Entry(models.Model):
    id = models.IntegerField(primary_key=True, max_length=50, editable=False)
    service_identifier= models.CharField(max_length=200)
    service = models.ForeignKey(Service)
    entry_date = models.DateTimeField(default=datetime.now)
    raw_json = models.TextField(blank=True)
    
    def __unicode__(self):
      service = Service.objects.get(service=self.service)
      return str(self.id)+' -- (' +str(service)+')'
    class Meta: 
      verbose_name_plural = "Entries"
	