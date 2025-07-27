from fastapi import FastAPI, Request, Depends, File, UploadFile
from pydantic import BaseModel #like requests from flask
import numpy as np
import tweepy
import joblib
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware
from backend.ratelimiter import RateLimiter
import os 
from google import genai
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

origins = ["https://localhost",
           "https://localhost:8000", "http://localhost:3000", "http://127.0.0.1:3000"]
app = FastAPI()
#frontend sends a preflight security check OPTIONS request need to 
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,  # Added Vite default port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


consumer_key =os.getenv("api_key")
consumer_secret =os.getenv("api_secret")
bearer_token= os.getenv("bearer_token")
access_token =os.getenv("access_token")
access_token_secret=os.getenv("access_token_secret")

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    bearer_token=bearer_token
)

auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

rate = api.rate_limit_status()
print(rate['resources']['media']['/media/upload'])
print(rate['resources']['tweets&POST']['/tweets&POST'])

gemini_key=os.getenv("GEMINI_API_KEY")
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
gem_client = genai.Client(api_key=gemini_key)

model = SentenceTransformer('sentence-transformers/paraphrase-albert-small-v2')

EMBEDDINGS_PATH = "models/events.npy"
DOCUMENT_PATH = "scripts/sportsevents.txt"


#need to be refreshed when agent runs
embeddings = None
events = None

#convert the JSON query to a string
class QueryRequest(BaseModel):
    query: str

class ImageRequest(BaseModel):
    query: str
    image_path: str

def load_embeddings():
    global embeddings, events
    embeddings = np.load(EMBEDDINGS_PATH)
    with open(DOCUMENT_PATH, "r") as f:
        content = f.read()
    #do same operation to split events into chunks
    events = content.split('Event:')[1:]
    events = [f"Event:{event.strip()}" for event in events]



#first api request POST, send user input

@app.get("/")
def home():
    return {"message": "Hello! This is the home page."}


@app.post("/gentweet", dependencies=[Depends(RateLimiter(requests_limit = 10, time_window=60))])
def get_events(request: QueryRequest): #request is the query
    
    query = request.query.strip()

    if not query:
        return {"error": "Query is required"}, 400

    query_embedding = model.encode(query)

    
    top_results = util.semantic_search(query_embedding, embeddings, top_k=1)[0] #[0] to remove the query number so only have tensor scores 
    context = []
    for res in top_results:
        idx = res['corpus_id']

        context.append({
            "event": events[idx]
        })
    today = date.today()
    prompt = f"""Generate an original and creative tweet for the event: {query}. Using this context {context}
        - The tweet must be under 2 sentences, under 280 characters, and use relevant hashtags.
        - Mention the event date in 'Month Day' format (e.g., July 24).
        - Get event date, compare it with todays date: {today}, determine if its before, matches, or after then
        - If event date in the context is before {today}, use correct past tense grammar. Use a tone that encourages users to relive or rewatch the event.
        - If event date in the context matches this date: {today}, use an urgent and immediate tone, announcing that the event is live or happening now.
        - If event date in the context is after this date: {today}, use a forward-looking tone that builds hype and anticipation.
        - The tweet must include a call to action to watch it at no cost/no charge/without paying and without chatboxes or popup ads using my Google Extension.
        - End with the phrase: "Link in bio." 
        - Do not mention FREE
        - Be creative but not random"""
 
    response = gem_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return {"tweet": response.text}

@app.post("/posttweet")
def post_tweet(request: QueryRequest): #request is the query
    query = request.query.strip()
    client.create_tweet(text=query)

@app.post("/posttweetwithimage")
def post_tweet_with_image(request: ImageRequest):
    image_path = request.image_path
    if not os.path.exists(image_path):
        return {"error": "Image file not found"}, 400
    query = request.query.strip()
    media = api.media_upload(image_path)

    client.create_tweet(text=query, media_ids=[media.media_id])




@app.post("/refresh")
def refresh_embeddings():
    load_embeddings()

#to run do uvicorn backend.app:app --reload , dont use reload if testing test cases