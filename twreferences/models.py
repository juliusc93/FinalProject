from django.contrib.gis.db import models
# Create your models here.


class Place(models.Model):
    place_id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=100)
    coordinates = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name


class User(models.Model):
    userid = models.CharField(max_length=60, primary_key=True)
    screen_name = models.CharField(max_length=60)
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
    # created_at = models.DateTimeField(blank=True, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        extra = "..."
        if len(self.content) < 5:
            extra = ""
        return str(self.user) + ": " + self.content[:10] + extra