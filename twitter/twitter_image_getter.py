import os
import json
import urllib
import tweepy
from tqdm import tqdm

import twitter_access_key as tak

# アクセス情報
CONSUMER_API_KEYS = tak.CONSUMER_API_KEYS
CONSUMER_SECRET_KEY = tak.CONSUMER_SECRET_KEY
ACCESS_TOKEN = tak.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = tak.ACCESS_TOKEN_SECRET

# 保存先
OUTPUT_DIR = './images/'

# 最大ページネーション数
PAGES = 10

class ImageDownloader():
  def __init__(self):
    auth = tweepy.OAuthHandler(CONSUMER_API_KEYS, CONSUMER_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    self.api = tweepy.API(auth)

  def search(self, user_id=None):
    try:
      if(user_id is None):
        raise Exception('user_id is None')
      
      max_id = None
      media_url_set = set()
      for page in tqdm(range(PAGES)):
        if(max_id is None):
          search_results = self.api.user_timeline(
              id=user_id, count=100, page=page)
        else:
          search_results = self.api.user_timeline(
              id=user_id, count=100, page=page, max_id=max_id)
        for result in search_results:
          if('media' in result.entities):
            for media in result.entities['media']:
              media_url_set.add(media['media_url_https'])
          max_id = result.id
      return list(media_url_set)
    except Exception as e:
      print(e)
    
  def download(self, urls, user_id):
    try:
      if (not os.path.exists(OUTPUT_DIR)):
        os.makedirs(OUTPUT_DIR)
      
      if (not os.path.exists(OUTPUT_DIR + user_id)):
        os.makedirs(OUTPUT_DIR + user_id)

      for url in tqdm(urls):
        filename = url.split('/')[-1]
        with urllib.request.urlopen(url) as file:
          img = file.read()
          with open(OUTPUT_DIR + user_id + '/' + filename, mode='wb') as f:
            f.write(img)
    except Exception as e:
      print(e)

  def run(self, user_id=None):
    self.download(self.search(user_id), user_id)


def main():
  img_downloader = ImageDownloader()
  img_downloader.run('')

if __name__ == '__main__':
  main()
