import argparse
# import json
import re
import requests
import os

TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')

parser = argparse.ArgumentParser()
parser.add_argument('--twitter_handle', dest='twitter_handle')

par = parser.parse_args()

def create_url():
    tweet_fields = "tweet.fields=lang,author_id,text"
    media_fields = "media.fields=url"
    user_fields = "user.fields=created_at,id,name,public_metrics,username,verified"
    query = f"query=from%3A{par.twitter_handle}%20(%22%40mastodon.social%22%20OR%20%22%40mas.to%22%20OR%20%22%40mastodon.art%22)%20has%3Alinks%20-is%3Aretweet"
    max_results = "max_results=100"
    url = f"https://api.twitter.com/2/tweets/search/recent?{query}&{max_results}&{tweet_fields}&expansions=author_id&{media_fields}&{user_fields}"
    return url

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r

# with open('/home/tuna/Documents/tweets.json') as json_file:
#     data = json.load(json_file)

#extract the link
def Find(string):
  
    # findall() has been used 
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)      
    return [x[0] for x in url]


def main():
    try:
        res = requests.request('GET', url=create_url(), auth=bearer_oauth)
        print(res.json())
    except Exception as e:
        print(f'Something went wrong: {e}')


    for tweet in res.json()['data']:
        for user in res.json()['includes']['users']:
        
            mastodon_links = Find(tweet['text'])
            for link in mastodon_links:
                try:
                    mas_res = requests.request('GET', url=link)
                    if "mas.to/@" or "mastodon.social/@" or "mastodon.art/@" in mas_res.url:
                        mastodon_handle = mas_res.url
                        twitter_followers = user['public_metrics']['followers_count']
                        result = f'{par.twitter_handle} with {twitter_followers} followers -> {mastodon_handle}'
                        print(result)
                    else:
                        print("wrong link")
                except Exception as e:
                    print(f'Error {e}')
        

if __name__ == "__main__":
    main()