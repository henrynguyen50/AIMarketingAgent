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


api_key =os.getenv("api_key")
api_secret =os.getenv("api_secret")
bearer_token= os.getenv("bearer_token")
access_token =os.getenv("access_token")
access_token_secret=os.getenv("access_token_secret")

client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

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
    print(context)
    today = date.today()
    prompt = f"Generate tweet: {query}, using this context {context}, watch it free and without chatboxes or popup ads using my Google Extension. Link in bio. If event date is {today} say that it is upcoming. If the events date does not match {today} say that it was in the past. Always mention the date(and change it to Month Day, like April 1st) and access to free sites, chatboxes, and clickon ads. Never use () or \n. Creative without being random,use hashtags, and try to keep tweet under 2 sentences"
 
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