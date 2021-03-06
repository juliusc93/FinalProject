from .models import Tweet, User, Place
from requests_oauthlib import OAuth1
from django.contrib.gis.geos import Point

import re
import requests
# Authentication key
AUTH = OAuth1("2cVrQhHKw0x34H9EAyzkMZ7aw",
              "hsl8tfWm2SMOwqjarDfCIkkbpp6Zvrl9syP4OnSzxprUYZtfgP")

""" To succesfully obtain the geo from instagram (and swarmapp) tweets, it was necessary to call the API for assistance.
    However, combining both scraping and API calls for each tweet to obtain its geo resulted in really, reaaaaaaally
    reaaaaaaallllllllllyyyyyyyyyyyy (emphasis) slow and painful performance in terms of computational complexity.

    Under such circumstances, I was forced to make a choice, and using the API to do all the job (without scraping)
    resulted in a cleaner, faster performance, as desired.
    Plus, the code below looks nicer, more "Pythonic".
"""


def get_user_tweets(username):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?count=50&include_rts=false" + \
          "&screen_name=" + username
    response = requests.get(url, auth=AUTH)
    json = response.json()

    if response.status_code == 200:
        user = User(userid=username, screen_name=json[0]["user"]["name"])
        if user not in User.objects.all():
            user.save()

        for elem in json:
            text = elem["text"]
            try:
                # Longitude: X, Latitude: Y; GeoDjango requires these values to be inserted IN THAT order
                # to accurately measure distances and make queries based on them.
                # However, the JSON lists the coordinates in (Latitude, Longitude) ...
                # That's why we call the reverse function.
                location = Point(list(reversed(elem["geo"]["coordinates"])))
            except:
                location = None
            
            if elem["place"] is not None:
                try:
                    place = Place.objects.get(place_id=elem["place"]["id"])
                except:
                    place = Place(place_id=elem["place"]["id"], name=elem["place"]["full_name"])
                    place.save()
            else:
                place = None
                
            if not Tweet.objects.filter(user=username, content=text):
                Tweet.objects.create(
                    user=user, content=text, kind="by_user", place=place, location=location)

    return response.status_code


def get_tweets(soup, kind, place=None):
    scrap = soup.select(
        "li.js-stream-item.stream-item.stream-item.expanding-stream-item")
    # To try to obtain the geo for each tweet
    for tweet in scrap:
        # This easily messed up my work, finally it's fixed.
        if not tweet.find("p", class_="bio "):
            header = tweet.find("div", class_="stream-item-header")
            userid = header.find("b").get_text()
            screen_name = header.find("strong").get_text()
            # This cleans the "Verified account" on the screen_name.
            screen_name = re.sub(r'\n.*', '', screen_name, re.MULTILINE)
            text = tweet.find("p", class_="TweetTextSize").get_text()
            user = User(userid=userid, screen_name=screen_name)
            if user not in User.objects.all():
                user.save()

            if not Tweet.objects.filter(user=user, content=text):
                Tweet.objects.create(
                    user=user, content=text, kind=kind, place=place)


def get_mentions(username):
    mention = re.compile("@\w+")
    tweets = Tweet.objects.filter(user=username, kind="by_user")
    mentions = []

    for tweet in tweets:
        query = re.findall(mention, tweet.content)
        for elem in query:
            if elem[1:] not in mentions:
                mentions.append(elem[1:])

    return mentions


def get_possible_places(username):
    place = re.compile("@ \w+((( ?(- )?)|, )(\w))+")  # Fix the regex
    tweets = Tweet.objects.filter(user=username, kind="by_user")
    places = []

    for tweet in tweets:
        query = re.findall(place, tweet.content)
        print query
        for elem in query:
            if elem not in places:
                places.append(elem)
    return places


def tweets2js(username):
    query = Tweet.objects.filter(user=username).exclude(location=None)
    coords = [{'lat': tweet.location.y, 'lng': tweet.location.x} for tweet in query]
    info = [tweet.content.encode("utf-8") for tweet in query]
    return {'info': info, 'coordinates': coords}


"""
 HTML Scraping is very unreliable for this task, as each Twitter page has a lot of <span class="Icon--verified"> tags
 in the markup which could mean anything (i.e. a verified account, verified accounts in "People to Follow", etc.).
 Plus, the markup always* has the following tag, hidden somewhere for internal purposes (?):
    <span class="u-hiddenVisually">Verified account</span>

 Which, with all the above, would yield lots of false positives, thus making it an unreliable approach.
 So we'll just use the Twitter API to facilitate this task.

 *Thus far, I haven't come across an example that displays the opposite.
"""


def isCelebrity(username):
    url = "https://api.twitter.com/1.1/users/show.json?screen_name=" + username
    response = requests.get(url, auth=AUTH).json()
    return response["verified"]


def findTweets(user, mention):
    regex = re.compile("@" + mention)
    tweets = Tweet.objects.filter(user=user, kind="by_user")
    return [tweet for tweet in tweets if re.findall(regex, tweet.content)]
    

def mention_count(user, search):
    regex = re.compile("@" + search)
    tweets = Tweet.objects.filter(user=user, kind="by_user")
    return len([tweet for tweet in tweets if re.findall(regex, tweet.content)])

class Relationship:
    NULL = "There is no relationship at all between the studied people. (Remember celebrities and verified accounts are discarded in this project.)"
    WEAK = "There is some relationship between them, they have met at least once. They frequent some similar places but only seem " + \
           "to be loosely related."
    MEDIUM = "There is a relationship between them. They have met several times and probably have met in similar places. " + \
             "They could be an acquaintance or have a small friendship."
    LIKELY = "They are indeed related. They have a conversation frequently and frequent similar places."
    VERY_LIKELY = "They seem to be close or good friends, and often go to the same places together."


def findRelation(candidate, mention):
    if isCelebrity(mention) or get_user_tweets(mention) == 401:  # Just discard this
        return Relationship.NULL
    else:  # There may be something, then
        # candidate_tweets = Tweet.objects.filter(user=candidate).exclude(location=None)
        # mention_tweets = Tweet.objects.filter(user=mention).exclude(location=None)
        
        """
            nearbytweets = 0
            for item in candidate_tweets:
                counter = mention_tweets.filter(location__distance_lte=(item.point, 800)).count() # 500m
                nearbytweets = nearbytweets + counter
        """
        if mention_count(mention, candidate) == 0:
            return Relationship.WEAK
        elif mention_count(mention, candidate) <= 5:
            return Relationship.MEDIUM
        else:
            return Relationship.LIKELY
