# Django imports
from django.shortcuts import render, redirect
from .models import Tweet, Place, User

# Other imports
from bs4 import BeautifulSoup
from .tools import get_tweets, get_mentions, isCelebrity, AUTH, get_user_tweets, tweets2js
from .forms import PlaceForm, UserForm
import requests

# Create your views here.


def set_place(request):
    places = None

    if request.method == "POST":
        form = PlaceForm(request.POST)
        if form.is_valid():  # List with all possible places matching the query
            url = "https://api.twitter.com/1.1/geo/search.json?query=" + \
                form.cleaned_data['place']
            response = requests.get(url, auth=AUTH, headers={'Connection':'close'}).json()
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


def searchuser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            return redirect("/user/"+form.cleaned_data['user'].strip())
    else:
        form = UserForm()
    return render(request, 'twreferences/search_user.html', {'form': form })
    
    
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
    status = get_user_tweets(username)
    if status == 401:  # Not authorized
        return render(request, "twreferences/protected.html", {})
    
    elif status == 404: # Not found
        return render(request, "twreferences/not_found.html", {})
    
    else:
        tweets = Tweet.objects.filter(user=username, kind="by_user")
        mentions = get_mentions(username)
        # places = get_possible_places(username)
        celeb = isCelebrity(username)
        return render(request, 'twreferences/tweet_user.html', {'user': username,
                                                                'tweets': tweets,
                                                                'mentions': mentions,
                                                                'celebrity': celeb,
                                                                'geotweets': Tweet.objects.filter(user=username).exclude(location=None).count()
                                                                })


def relation(request, candidate, mention):
    from .tools import findRelation, mention_count, findTweets
    if not Tweet.objects.filter(user=mention):
        get_user_tweets(mention)

    tw_candidate = tweets2js(candidate)
    tw_mention = tweets2js(mention)

    return render(request, 'twreferences/relationship.html', {'candidate': candidate,
                                                              'mention': mention,
                                                              'relation': findRelation(candidate, mention),
                                                              'tw_candidate': tw_candidate,
                                                              'tw_mention': tw_mention,
                                                              'list_candidate': Tweet.objects.filter(user=candidate),
                                                              'list_mention': Tweet.objects.filter(user=mention),
                                                              'filter_candidate': findTweets(candidate, mention),
                                                              'filter_mention': findTweets(mention, candidate),
                                                              'count1': mention_count(candidate, mention),
                                                              'count2': mention_count(mention, candidate),
                                                              })


def test(request):
    return render(request, 'twreferences/relationship.html', {})