from .models import Tweet, User
from requests_oauthlib import OAuth1
import re
import requests

# Authentication key
AUTH = OAuth1("en5VXgZ5CLDJ5y1N5nhbByqa8",
              "JjsMi4ijOeaB2qMkTWTns1VMIRetaD9eb6yggmEtKBCSQ2G6Dx")


def get_tweets(soup, kind, place=None):
    scrap = soup.select(
        "li.js-stream-item.stream-item.stream-item.expanding-stream-item")
    for tweet in scrap:
        # This easily messed up my work, finally it's fixed.
        if not tweet.find("p", class_="bio "):
            header = tweet.find("div", class_="stream-item-header")
            userid = header.find("b").get_text()
            screen_name = header.find("strong").get_text()
            text = tweet.find("p", class_="TweetTextSize").get_text()
            user = User(userid=userid, screen_name=screen_name)
            if user not in User.objects.all():
                user.save()

            if not Tweet.objects.filter(user=user, content=text, kind=kind):
                Tweet.objects.create(
                    user=user, content=text, kind=kind, place=place)


def get_mentions(username):
    mention = re.compile("@\w+")
    tweets = Tweet.objects.filter(user=username, kind="by_user")
    mentions = []
    # If the person has twitted more than once, we'll store all the mentions in a unique entry. A dictionary accomplishes this task.
    # Plus, we'll remove duplicate mentions, if any.
    # We'll just use list comprehension for this.

    # return [ list(set(re.findall(mention, tweet.content))) for tweet in
    # tweets ]
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
    auth = OAuth1("en5VXgZ5CLDJ5y1N5nhbByqa8",
                  "JjsMi4ijOeaB2qMkTWTns1VMIRetaD9eb6yggmEtKBCSQ2G6Dx")
    url = "https://api.twitter.com/1.1/users/show.json?screen_name=" + username
    response = requests.get(url, auth=auth).json()
    return response["verified"]


def mention_count(user, search):
    regex = re.compile("@\w+")
    tweets = Tweet.objects.filter(user=user, kind="by_user")
    mentions = [re.findall(regex, tweet.content) for tweet in tweets]
    """
     As re.findall() may return sublists, we'll convert mentions to a flat
     list, then count the occurrences over it
    """
    return [item for sublist in mentions for item in sublist].count(search.userid)


class Relationship:
    NULL = 0
    WEAK = 1
    MEDIUM = 2
    LIKELY = 3
    VERY_LIKELY = 4


def findRelation(candidate, mention):
    if isCelebrity(mention.userid) is False:  # Just discard this
        return Relationship.NULL
    else:  # There may be something, then
        if mention_count(mention, candidate) == 0:
            pass
        elif mention_count(mention, candidate) <= 5:
            pass
        else:
            pass
