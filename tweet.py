import tweepy
import os 
import requests
from google import genai
from dotenv import load_dotenv
load_dotenv()
api_key =os.getenv("api_key")
api_secret =os.getenv("api_secret")
bearer_token= os.getenv("bearer_token")
access_token =os.getenv("access_token")
access_token_secret=os.getenv("access_token_secret")


client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

import requests

api_url = "http://127.0.0.1:8000/gentweet"

payload = {
    "query": "Make a tweet for stardom"
}

try:
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        print("Success! API Response:")
        # Print the JSON data returned by the API
        res = response.json()
        tweet = res['tweet']
        tweet = tweet.strip() 
        client.create_tweet(text=tweet)
    else:
        print(f"Error: Received status code {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the server at {api_url}.")
    print("Please make sure your FastAPI server is running.")


