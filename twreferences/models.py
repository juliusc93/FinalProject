from django.db import models

# Create your models here.
class Place(models.Model):
	place_id = models.CharField(max_length=16, primary_key=True)
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

class Tweet(models.Model):
    user = models.CharField(max_length=30)
    content = models.TextField()
    kind = models.CharField(max_length=30)
    place = models.ForeignKey(Place, blank=True, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
    	extra = "..."
    	if len(self.content) < 5:
    		extra = ""
    	return self.user + ": " + self.content[:5] + extra

