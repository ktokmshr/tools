import re

import tweepy
from comiket import twitter_access_key as tak

CONSUMER_API_KEYS = tak.CONSUMER_API_KEYS
CONSUMER_SECRET_KEY = tak.CONSUMER_SECRET_KEY
ACCESS_TOKEN = tak.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = tak.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_API_KEYS, CONSUMER_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
my_info = api.me()

follow_ids = []
for friend_id in tweepy.Cursor(api.friends_ids, user_id=my_info.id).items():
	follow_ids.append(friend_id)

comiket_user = []
for i in range(0, len(follow_ids), 100):
	for user in api.lookup_users(user_ids=follow_ids[i:i+100]):
		if bool(re.search('.*(東|西|南).*[0-9０-９].*', user.name)):
			comiket_user.append(user.name)

with open('./comiket.txt', mode='w') as output:
	output.write('\n'.join(comiket_user))
