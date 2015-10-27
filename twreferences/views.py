# Django imports
from django.shortcuts import render
from .models import Tweet, Place, User

# Other imports
from bs4 import BeautifulSoup
from .tools import get_tweets, get_mentions, get_possible_places, isCelebrity, AUTH, get_user_tweets
from .forms import PlaceForm
import requests

# Create your views here.


def set_place(request):
    places = None

    if request.method == "POST":
        form = PlaceForm(request.POST)
        if form.is_valid():  # List with all possible places matching the query
            url = "https://api.twitter.com/1.1/geo/search.json?query=" + \
                form.cleaned_data['place']
            response = requests.get(url, auth=AUTH).json()
            query = response["result"]["places"]

            # Store the places in our database
            places = []
            for place in query:
                p = Place(place_id=place["id"], name=place["full_name"])
                # Don't save it more than once
                if p not in Place.objects.all():
                    p.save()
                places.append(p)
    else:
        form = PlaceForm()
    return render(request, 'twreferences/select_place.html', {'form': form, 'results': places})


def tweetlist(request, place_id):
    Tweet.objects.filter(kind="by_place").delete()
    url = "https://twitter.com/search?q=place%3A" + place_id + "&lang=en"
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content)
    place = Place.objects.get(place_id=place_id)
    get_tweets(soup, "by_place", place=place)
    tweets = Tweet.objects.filter(kind="by_place")
    return render(request, 'twreferences/tweetlist.html', {'tweets': tweets,
                                                           'url': url,
                                                           'name': place.name
                                                           })


def tweet_user(request, username):
    if get_user_tweets(username) == 401:  # Not authorized
        return render(request, "twreferences/protected.html", {})

    tweets = Tweet.objects.filter(user=username, kind="by_user")
    mentions = get_mentions(username)
    places = get_possible_places(username)
    celeb = isCelebrity(username)
    return render(request, 'twreferences/tweet_user.html', {'user': username,
                                                            'tweets': tweets,
                                                            'mentions': mentions,
                                                            'places': places,
                                                            'celebrity': celeb,
                                                            })


def relation(request, user1, user2):
    from .tools import findRelation
    candidate = User.objects.get(userid=user1)
    if not Tweet.objects.filter(user=user2):
        get_user_tweets(user2)
    mention = User.objects.get(userid=user2)
    return render(request, 'twreferences/relationship.html', {'relation': findRelation(candidate, mention)})


def test(request):
    tweets = Tweet.objects.exclude(location=None)
    return render(request, 'twreferences/maptest.html', {'tweets': tweets})
