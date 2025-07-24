import requests
from google import genai
import requests
import time
def genTestTweet():
    try:
        gen_api_url = "http://127.0.0.1:8000/gentweet"

        topics = ["AEW", "WWE", "Stardom", "NJPW"]
        for promotion in topics:
            payload = {
                "query": f"Make a tweet for {promotion}"
            }
            response = requests.post(gen_api_url, json=payload)

            if response.status_code == 200:
                print("Success! API Response:")
                # Print the JSON data returned by the API
                res = response.json()
                tweet = res['tweet']
                tweet = tweet.strip() 
                print(tweet)

                
                
            else:
                print(f"Error: Received status code {response.status_code}")
                print("Response:", response.text)
            

    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to the server.")
        print("Please make sure your FastAPI server is running.")

if __name__ == "__main__":
    genTestTweet()