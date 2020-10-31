
from datetime import date
from os import stat
from django.utils.functional import Promise

from rest_framework.serializers import Serializer
from tweetme.settings import ALLOWED_HOSTS
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer, TweetActionSerializer, TweetCreateSerializer
ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# using jdango rest framework


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetCreateSerializer(data=request.POST)
    print(serializer)
    if(serializer.is_valid(raise_exception=True)):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response({}, status=400)


@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    tweets = Tweet.objects.all()
    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    tweets = Tweet.objects.filter(id=tweet_id)
    if not tweets.exists():
        return Response({}, status=404)
    tweet = tweets.first()

    serializer = TweetSerializer(tweet)
    return Response(serializer.data, status=200)


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    tweet = Tweet.objects.filter(id=tweet_id)
    if not tweet.exists():
        return Response({}, status=404)
    own_tweet = tweet.filter(user=request.user)
    if not own_tweet.exists():
        return Response({'message': 'you must login or not your tweet?'}, status=401)
    tweet = own_tweet.first()
    tweet.delete()
    return Response({'message': 'tweet removed'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    """
    id is required
    acttion are : like,unlike,retweet
    """
    print(request.POST, request.data)
    serialzer = TweetActionSerializer(data=request.data)
    if serialzer.is_valid(raise_exception=True):
        data = serialzer.validated_data
        tweet_id = data.get("id")
        action = data.get("action")

        tweet = Tweet.objects.filter(id=tweet_id)
        if not tweet.exists():
            return Response({}, status=404)
        tweet = tweet.first()
        if action == 'like':
            tweet.likes.add(request.user)
            # formated data in key value pair
            serializer = TweetSerializer(tweet)
            # print(serializer.data) json data
            return Response(serializer.data, status=200)
        elif action == 'unlike':
            tweet.likes.remove(request.user)
        elif action == 'retweet':
            # this is todo
            new_tweet = Tweet.objects.create(user=request.user,
                                             parent=tweet,
                                             content=tweet.content)
            serializer = TweetSerializer(new_tweet)
            print('serial = ', serializer.data)
            return Response(serializer.data, status=201)

    return Response({}, status=200)

# pure django


def home_view(request, *args, **kwrags):
    template_name = 'pages/home.html'
    return render(request, template_name, context={})


def tweet_list_view_puredjango(request, *args, **kwargs):

    tweets = Tweet.objects.all()
    tweet_list = [x.serialize() for x in tweets]
    data = {
        "response": tweet_list
    }
    return JsonResponse(data)


def tweet_detail_view_puredjango(request, tweet_id):
    """ 
    rest api view
    """

    data = {
        'id': tweet_id,
    }
    status = 200

    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
    except:
        data['message'] = 'not found'
        status = 404

    return JsonResponse(data, status=status)


def tweet_create_view_purejdango(request, *args, **kwargs):

    if not request.user.is_authenticated:
        print(request.user)
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)

    template_name = 'components/form.html'
    form = TweetForm(request.POST or None)
    print(request.is_ajax())
    next_url = request.POST.get("next") or None

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)
        if(next_url != None) and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)

    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
        # form = TweetForm()
    return render(request, template_name, context={'form': form})
