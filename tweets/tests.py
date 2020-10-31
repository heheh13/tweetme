from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import client
from django.utils.functional import Promise
from rest_framework import response
from .models import Tweet
from rest_framework.test import APIClient
User = get_user_model()

# Create your tests here.


class TweetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='heheh', password='heheh')
        Tweet.objects.create(content='my first twwet', user=self.user)
        Tweet.objects.create(content='my second twwet', user=self.user)
        Tweet.objects.create(content='my third twwet', user=self.user)

    def test_tweet_crated(self):
        tweet = Tweet.objects.create(content='my twwet', user=self.user)
        self.assertEqual(tweet.id, 4)
        self.assertEqual(tweet.user, self.user)

    def get_client(self):
        client = APIClient()
        client.login(username=self.user.username, password="heheh")
        return client

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get("/api/tweets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_action_like(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/",
                               {"id": 1, "action": "like"})
        self.assertEqual(response.status_code, 200)
        # print(response.json())
