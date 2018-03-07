# -*- coding: utf-8 -*-
import os, string
import time, tweepy, json

consumer_key="QMM9pAjHKYRQ4gMGNbNRDugHu"
consumer_secret="00uRXAzclsmQE0MjR5LYOhwZJPfJQaXBmNJJ4gI9bZfGEwi286"
access_token="1170470796-W0IQzj5X4NAZZ0WN6dGic7cUeBSX3jhbJlCAwkG"
access_token_secret="kfhFd1Uw2cOfojmWLyoT3myF3LUmA6GcbXKelE6nuOKNK"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


class FilteredStream(tweepy.StreamListener):
        def on_status(self,status):
            if type(status.geo)!=type(None):
                print("{0},{1},{2},{3},{4}".format(status.id_str,status.text.replace(',','^^^').strip('\n'),status.geo['coordinates'][0],status.geo['coordinates'][1],status.created_at))

streamListener = FilteredStream()
stream = tweepy.Stream(auth=api.auth,listener=streamListener)
stream.filter(locations=[-124,24,-66,49])



