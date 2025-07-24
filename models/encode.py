import numpy as np
from sentence_transformers import SentenceTransformer
import joblib


model = SentenceTransformer('sentence-transformers/paraphrase-albert-small-v2')

file_path='scripts/sportsevents.txt'
def encode_events():
    with open(file_path, 'r') as f:
        document= f.read()

    events = document.split('Event:')[1:] #first element always empty after split
    cleaned_events = [] #seperate chunks of text into the list
    for event in events:
        event_text = f"Event:{event.strip()}" #add event back
        cleaned_events.append(event_text)


    print("Making embeddings")
    embeddings = model.encode(cleaned_events)

    #save embeddings then dataframe 
    np.save("models/events.npy", embeddings)
    print("Embeddings saved")
    print(embeddings.shape)

if __name__ == "__main__":
    encode_events()