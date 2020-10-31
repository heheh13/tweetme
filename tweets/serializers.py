from os import read
from django.conf import settings
from rest_framework import serializers
from rest_framework.decorators import action
from .models import Tweet

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTION_OPTIONS = settings.TWEET_ACTION_OPTIONS


class TweetActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    comment = serializers.CharField(allow_blank=True, required=False)

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError(
                "this is not a valid action for tweets")
        return value


class TweetCreateSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes']

    def get_likes(self, tweet):
        return tweet.likes.count()

    def validate_content(self, content):

        if len(content) > MAX_TWEET_LENGTH:
            raise serializers.ValidationError('tweet too large')
        return content


class TweetSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    parent = TweetCreateSerializer(read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes', 'is_retweet', 'parent']

    def get_likes(self, tweet):
        return tweet.likes.count()

    # def get_content(self, tweet):
    #     content = tweet.content
    #     if tweet.is_retweet:
    #         content = tweet.parent.content
    #     return content
