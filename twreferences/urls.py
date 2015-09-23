from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.set_place, name="set_place"),
	url(r'^places/(?P<place_id>[a-f0-9]{16})$', views.tweetlist, name='tweetlist'),
	url(r'^user/(?P<username>[a-zA-Z0-9_]+)/$', views.tweet_user, name='tweet_user'),
]