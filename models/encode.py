import numpy as np
from sentence_transformers import SentenceTransformer
import joblib


model = SentenceTransformer('sentence-transformers/paraphrase-albert-small-v2')

file_path='scripts/sportsevents.txt'

with open(file_path, 'r') as f:
    document= f.readlines()

print("Making embeddings")
embeddings = model.encode(document)

#save embeddings then dataframe 
np.save("models/events.npy", embeddings)
print("Embeddings saved")
print(embeddings.shape)