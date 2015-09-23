from bs4 import BeautifulSoup
from .models import Tweet
import re

def get_tweets(soup, kind):
	scrap = soup.select("li.js-stream-item.stream-item.stream-item.expanding-stream-item")
	for tweet in scrap:
		if not tweet.find("p", class_="bio "): #This easily messed up my work, finally it's fixed.
			header = tweet.find("div", class_="stream-item-header")
			userid = header.find("b").get_text()
			text = tweet.find("p", class_="TweetTextSize").get_text()
			if not Tweet.objects.filter(user=userid, content=text, kind=kind):
				Tweet.objects.create(user=userid, content=text, kind=kind, place=None)

def get_mentions(username):
	mention = re.compile("@\w+")
	tweets = Tweet.objects.filter(user=username, kind="by_user")
	mentions = []
	#If the person has twitted more than once, we'll store all the mentions in a unique entry. A dictionary accomplishes this task.
	#Plus, we'll remove duplicate mentions, if any. 
	#We'll just use list comprehension for this.

	#return [ list(set(re.findall(mention, tweet.content))) for tweet in tweets ]
	for tweet in tweets:
		query = re.findall(mention, tweet.content)
		for elem in query:
			if elem[1:] not in mentions:
				mentions.append(elem[1:])

	return mentions

def get_possible_places(username):
	place = re.compile("@ \w+((( ?(- )?)|, )(\w))+") # Fix the regex
	tweets = Tweet.objects.filter(user=username, kind="by_user")
	places = []

	for tweet in tweets:
		query = re.findall(place, tweet.content)
		print query
		for elem in query:
			if elem not in places:
				places.append(elem)
	return places