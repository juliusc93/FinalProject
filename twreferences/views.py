 # Django imports
from django.shortcuts import render
from .models import Tweet
# Other imports
from bs4 import BeautifulSoup
import random, re, requests, json
from requests_oauthlib import OAuth1
from .tools import get_tweets, get_mentions, get_possible_places

# Create your views here.
def tweetlist(request):
	Tweet.objects.filter(kind="by_place").delete()
	auth = OAuth1("en5VXgZ5CLDJ5y1N5nhbByqa8", "JjsMi4ijOeaB2qMkTWTns1VMIRetaD9eb6yggmEtKBCSQ2G6Dx")
	url = "https://api.twitter.com/1.1/geo/search.json?query=Barranquilla"
	r = requests.get(url, auth=auth)
	test = r.json()
	place_id = test["result"]["places"][0]["id"]
	place_name = test["result"]["places"][0]["full_name"]
	url = "https://twitter.com/search?q=place%3A"+place_id+"&lang=en"
	webpage = requests.get(url)
	soup = BeautifulSoup(webpage.content)
	get_tweets(soup, "by_place")
	tweets = Tweet.objects.filter(kind="by_place")
	return render(request, 'twreferences/tweetlist.html', {'tweets': tweets, 'url': url, 'name': place_name})

def tweet_user(request, username):
	url = "https://twitter.com/" + username + "?count=50"
	user_webpage = requests.get(url)
	soup = BeautifulSoup(user_webpage.content)
	if soup.find("div", class_="ProtectedTimeline"):
		return render(request, 'twreferences/protected.html', {})
	get_tweets(soup, "by_user")

	tweets = Tweet.objects.filter(user=username, kind="by_user")
	mentions = get_mentions(username)
	places = get_possible_places(username)
	return render(request, 'twreferences/tweet_user.html', {'user': username, 
		'tweets': tweets, 
		'mentions': mentions,
		'places': places,
		})