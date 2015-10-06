from django.contrib.gis.db import models
from requests_oauthlib import OAuth1
import requests
# Create your models here.


class Place(models.Model):
    place_id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=100)
    coordinates = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name


class User(models.Model):
    userid = models.CharField(max_length=30, primary_key=True)
    screen_name = models.CharField(max_length=30)
    is_candidate = models.BooleanField(default=False)
    related_to = models.ForeignKey("self", blank=True, null=True)

    def __unicode__(self):
        return self.userid


class Tweet(models.Model):
    user = models.ForeignKey(User)
    content = models.TextField()
    kind = models.CharField(max_length=30)
    place = models.ForeignKey(Place, blank=True, null=True, on_delete=models.SET_NULL)
    location = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        extra = "..."
        if len(self.content) < 5:
            extra = ""
        return str(self.user) + ": " + self.content[:10] + extra

    def has_geo(self):
        AUTH = OAuth1("en5VXgZ5CLDJ5y1N5nhbByqa8",
                      "JjsMi4ijOeaB2qMkTWTns1VMIRetaD9eb6yggmEtKBCSQ2G6Dx")
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json?count=50&exclude_replies=true&include_rts=false" + \
              "&screen_name=" + self.user.userid
        response = requests.get(url, auth=AUTH).json()
        return response["geo"] is None
