from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.tweetlist, name='tweetlist'),
	url(r'^user/(?P<username>[a-zA-Z0-9_]+)/$', views.tweet_user, name='tweet_user'),
]