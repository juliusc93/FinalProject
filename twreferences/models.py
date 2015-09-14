from django.db import models

# Create your models here.
class Tweet(models.Model):
    user = models.CharField(max_length=30)
    content = models.TextField()
    kind = models.CharField(max_length=30)

    def __unicode__(self):
    	extra = "..."
    	if len(self.content) < 5:
    		extra = ""
    	return self.user + ": " + self.content[:5] + extra

