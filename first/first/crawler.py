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
    def __init__(self,time_limit=60):
        self.start_time = time.time()
        self.limit = time_limit
        os.system("touch tmp_results")
        self.File = open("tmp_results.txt","r+")
        super(FilteredStream,self).__init__()
    
    def on_status(self,status):
        if (time.time() - self.start_time) < self.limit:
            if type(status.geo)!=type(None):
                self.File.write("{0},{1},{2},{3},{4}\n".format(status.id_str,status.text.replace(',','^^^').replace('\n',"").replace('-&gt',""),status.geo['coordinates'][0],status.geo['coordinates'][1],status.created_at))
            return True
        else:
            self.File.close()
            return False

os.system("touch tmp_results.txt")
stream = tweepy.Stream(auth=api.auth,listener=FilteredStream(time_limit=10))
stream.filter(locations=[-124,24,-66,49])
print("done")
