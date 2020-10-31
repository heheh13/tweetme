
from django.urls import path
from tweets.views import(
    tweet_detail_view,
    tweet_list_view,
    tweet_create_view,
    tweet_delete_view,
    tweet_action_view
)
'''
hey client
base enpoint for tweets start with api/tweets/
'''
urlpatterns = [
    path("tweets/", tweet_list_view, name='tweet_list'),
    path("tweets/action/", tweet_action_view, name='tweet-action'),
    path("tweets/<int:tweet_id>/", tweet_detail_view, name="tweet_detail"),
    path("tweets/<int:tweet_id>/delete/",
         tweet_delete_view, name="tweet_delete"),
    path("create/", tweet_create_view, name='tweet-create'),
]
