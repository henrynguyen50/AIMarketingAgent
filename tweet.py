import requests
from google import genai
import requests
import time
import os
def genTweet():
    try:
        gen_api_url = "http://127.0.0.1:8000/gentweet"

        topics = ["AEW", "WWE", "NJPW", "STARDOM"]
       

        for promotion in topics:
            payload = {
                "query": f"Make a tweet for {promotion},"
            }
            response = requests.post(gen_api_url, json=payload)
            # Look for image file with promotion name
            image_path = f"{promotion}.jpg"
            if response.status_code == 200:
                print("Success! API Response:")
                # Print the JSON data returned by the API
                res = response.json()
                tweet = res['tweet']
                tweet = tweet.strip() 
                print(tweet)

                
                if os.path.exists(image_path):
                    # Post tweet with image
                    tweet_api_url = "http://127.0.0.1:8000/posttweetwithimage"
                    tweet_payload = {
                        "query": tweet,
                        "image_path": image_path
                    }
                else:
                    # Post tweet without image
                    tweet_api_url = "http://127.0.0.1:8000/posttweet"
                    tweet_payload = {
                        "query": tweet
                    }

                response = requests.post(tweet_api_url, json=tweet_payload)
                if response.status_code == 200:
                    print("Tweet posted successfully.")
                
                else:
                    print(f"Error posting tweet: {response.status_code}")
                    print(response.text)
            else:
                print(f"Error: Received status code {response.status_code}")
                print("Response:", response.text)
            time.sleep(60)

    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to the server.")
        print("Please make sure your FastAPI server is running.")


if __name__ == "__main__":
    genTweet()