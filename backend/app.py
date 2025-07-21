from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel #like requests from flask
import numpy as np
import joblib
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware
from backend.ratelimiter import RateLimiter
import os 
from google import genai
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

gemini_key=os.getenv("GEMINI_API_KEY")
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
gem_client = genai.Client(api_key=gemini_key)



file_path='scripts/sportsevents.txt'
with open(file_path, 'r') as f:
    document= f.readlines()
#convert the JSON query to a string
class QueryRequest(BaseModel):
    query: str

print("load models")
model = SentenceTransformer('sentence-transformers/paraphrase-albert-small-v2')
embeddings = np.load("models/events.npy") #load mebeddings using numpy

#first api request POST, send user input

@app.get("/")
def home():
    return {"message": "Hello! This is the home page."}

@app.post("/gentweet", dependencies=[Depends(RateLimiter(requests_limit = 10, time_window=60))])
def get_events(request: QueryRequest): #request is the query
    query = request.query.strip()

    if not query:
        return {"error": "Query is required"}, 400

    #encode query using model
    query_embedding = model.encode(query)

    #now use cosine similarity to get closest movies
    
    top_results = util.semantic_search(query_embedding, embeddings, top_k=5)[0] #[0] to remove the query number so only have tensor scores 
    context = []
    for res in top_results:
        idx = res['corpus_id']

        context.append({
            "event": document[idx]
        })
    
    prompt = f"Generate tweet based off this: {query}, using this context {context}, should be like *event* is on *date* watch it free and without chatboxes or clickon ads using my extension Link in bio. Use correct past/present/future tense based on date, if event was in the past mention that. Always mention chatboxes and clickon ads. Never use () or \n. Be creative"

    response = gem_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return {"tweet": response.text}


#to run do uvicorn backend.app:app --reload , dont use reload if testing test cases